# phonebook.py
# Основное приложение телефонного справочника
import psycopg2
import json
import csv
from datetime import datetime
from connect import get_connection
from config import DB_CONFIG

class PhoneBook:
    """Класс для управления телефонным справочником"""
    
    def __init__(self):
        """Инициализация соединения с БД и параметров"""
        self.conn = get_connection()
        self.current_page = 1
        self.page_size = 5
        self.sort_by = 'name'
        
    def init_db(self):
        """Инициализация базы данных - создание таблиц и процедур"""
        try:
            with self.conn.cursor() as cur:
                # Выполняем schema.sql
                with open('schema.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
                
                # Выполняем procedures.sql
                with open('procedures.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
                
                self.conn.commit()
                print("Database initialized successfully")
        except Exception as e:
            print(f"Initialization error: {e}")
            self.conn.rollback()
    
    def add_contact(self, name, email=None, birthday=None, group_name='Other'):
        """Добавление нового контакта"""
        try:
            with self.conn.cursor() as cur:
                # Получаем group_id
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                group = cur.fetchone()
                if not group:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                    group_id = cur.fetchone()[0]
                else:
                    group_id = group[0]
                
                # Добавляем контакт
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, email, birthday, group_id))
                contact_id = cur.fetchone()[0]
                self.conn.commit()
                print(f"Contact '{name}' added with ID {contact_id}")
                return contact_id
        except Exception as e:
            print(f"Error adding contact: {e}")
            self.conn.rollback()
            return None
    
    def add_phone(self, contact_name, phone, phone_type):
        """Добавление телефона для контакта"""
        try:
            with self.conn.cursor() as cur:
                # Находим контакт по имени
                cur.execute("SELECT id FROM contacts WHERE name = %s", (contact_name,))
                contact = cur.fetchone()
                
                if contact:
                    contact_id = contact[0]
                    # Добавляем телефон напрямую через INSERT
                    cur.execute("""
                        INSERT INTO phones (contact_id, phone, type) 
                        VALUES (%s, %s, %s)
                    """, (contact_id, phone, phone_type))
                    self.conn.commit()
                    print(f"Phone {phone} added for {contact_name}")
                    return True
                else:
                    print(f"Contact '{contact_name}' not found. Please add contact first.")
                    return False
        except Exception as e:
            print(f"Error adding phone: {e}")
            self.conn.rollback()
            return False
    
    def move_to_group(self, contact_name, group_name):
        """Перемещение в группу"""
        try:
            with self.conn.cursor() as cur:
                # Находим контакт
                cur.execute("SELECT id FROM contacts WHERE name = %s", (contact_name,))
                contact = cur.fetchone()
                
                if not contact:
                    print(f"Contact '{contact_name}' not found")
                    return False
                
                contact_id = contact[0]
                
                # Находим или создаем группу
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                group = cur.fetchone()
                
                if not group:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                    group_id = cur.fetchone()[0]
                    print(f"Created new group: {group_name}")
                else:
                    group_id = group[0]
                
                # Обновляем группу контакта
                cur.execute("UPDATE contacts SET group_id = %s WHERE id = %s", (group_id, contact_id))
                self.conn.commit()
                print(f"Contact '{contact_name}' moved to group '{group_name}'")
                return True
        except Exception as e:
            print(f"Error moving contact: {e}")
            self.conn.rollback()
            return False
    
    def filter_by_group(self, group_name):
        """Фильтрация контактов по группе"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, c.name, COALESCE(c.email, '') as email, 
                           c.birthday, COALESCE(g.name, 'No Group') as group_name,
                           COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), 'No phones') as phones
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON c.id = p.contact_id
                    WHERE g.name = %s
                    GROUP BY c.id, g.name, c.name, c.email, c.birthday
                    ORDER BY c.name
                """, (group_name,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error filtering by group: {e}")
            return []
    
    def search_by_email(self, email_pattern):
        """Поиск по email с частичным совпадением"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, c.name, COALESCE(c.email, '') as email, 
                           c.birthday, COALESCE(g.name, 'No Group') as group_name,
                           COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), 'No phones') as phones
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON c.id = p.contact_id
                    WHERE c.email ILIKE %s
                    GROUP BY c.id, g.name, c.name, c.email, c.birthday
                    ORDER BY c.name
                """, (f'%{email_pattern}%',))
                return cur.fetchall()
        except Exception as e:
            print(f"Error searching by email: {e}")
            return []
    
    def search_contacts(self, query):
        """Расширенный поиск по всем полям"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT
                        c.id,
                        c.name,
                        COALESCE(c.email, '') as email,
                        c.birthday,
                        COALESCE(g.name, 'No Group') as group_name,
                        COALESCE(STRING_AGG(DISTINCT p.phone || ' (' || p.type || ')', ', '), 'No phones') as phones,
                        (
                            (CASE WHEN c.name ILIKE %s THEN 3 ELSE 0 END) +
                            (CASE WHEN c.email ILIKE %s THEN 2 ELSE 0 END) +
                            (CASE WHEN p.phone ILIKE %s THEN 2 ELSE 0 END)
                        ) as relevance
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON c.id = p.contact_id
                    WHERE 
                        c.name ILIKE %s OR
                        c.email ILIKE %s OR
                        p.phone ILIKE %s
                    GROUP BY c.id, g.name, c.name, c.email, c.birthday
                    ORDER BY relevance DESC, c.name
                """, (f'%{query}%', f'%{query}%', f'%{query}%', 
                      f'%{query}%', f'%{query}%', f'%{query}%'))
                return cur.fetchall()
        except Exception as e:
            print(f"Error searching contacts: {e}")
            return []
    
    def get_sorted_contacts(self, sort_by='name'):
        """Получение отсортированных контактов"""
        order_by = {
            'name': 'c.name',
            'birthday': 'c.birthday NULLS LAST',
            'date_added': 'c.created_at'
        }.get(sort_by, 'c.name')
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    SELECT 
                        c.id, 
                        c.name, 
                        COALESCE(c.email, '') as email,
                        c.birthday, 
                        COALESCE(g.name, 'No Group') as group_name,
                        COALESCE(STRING_AGG(DISTINCT p.phone || ' (' || p.type || ')', ', '), 'No phones') as phones
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON c.id = p.contact_id
                    GROUP BY c.id, g.name, c.name, c.email, c.birthday, c.created_at
                    ORDER BY {order_by}
                """)
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting sorted contacts: {e}")
            return []
    
    def paginate(self, page_num):
        """Получение страницы контактов"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.id, 
                        c.name, 
                        COALESCE(c.email, '') as email,
                        c.birthday, 
                        COALESCE(g.name, 'No Group') as group_name,
                        COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), 'No phones') as phones
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON c.id = p.contact_id
                    GROUP BY c.id, g.name, c.name, c.email, c.birthday
                    ORDER BY c.name
                    LIMIT %s
                    OFFSET %s
                """, (self.page_size, (page_num - 1) * self.page_size))
                return cur.fetchall()
        except Exception as e:
            print(f"Error in pagination: {e}")
            return []
    
    def export_to_json(self, filename='contacts_export.json'):
        """Экспорт всех контактов в JSON файл"""
        contacts = self.get_sorted_contacts()
        data = []
        for contact in contacts:
            data.append({
                'id': contact[0],
                'name': contact[1],
                'email': contact[2],
                'birthday': str(contact[3]) if contact[3] else None,
                'group': contact[4],
                'phones': contact[5]
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(data)} contacts to {filename}")
    
    def import_from_json(self, filename='contacts_export.json'):
        """Импорт контактов из JSON файла с обработкой дубликатов"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for contact in data:
                # Проверка на дубликат по имени
                with self.conn.cursor() as cur:
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (contact['name'],))
                    existing = cur.fetchone()
                    
                    if existing:
                        print(f"Contact '{contact['name']}' already exists")
                        choice = input("Skip (s) or overwrite (o)? ").lower()
                        if choice == 'o':
                            # Удаляем существующий контакт
                            cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                            self.conn.commit()
                        else:
                            continue
                
                # Добавляем контакт
                self.add_contact(
                    name=contact['name'],
                    email=contact.get('email'),
                    birthday=contact.get('birthday'),
                    group_name=contact.get('group', 'Other')
                )
            print("Import completed successfully")
        except Exception as e:
            print(f"Import error: {e}")
    
    def import_from_csv(self, filename='contacts.csv'):
        """Импорт контактов из CSV файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    contact_id = self.add_contact(
                        name=row['name'],
                        email=row.get('email'),
                        birthday=row.get('birthday') if row.get('birthday') else None,
                        group_name=row.get('group', 'Other')
                    )
                    if contact_id and row.get('phone'):
                        self.add_phone(row['name'], row['phone'], row.get('phone_type', 'mobile'))
            print("CSV import completed successfully")
        except Exception as e:
            print(f"CSV import error: {e}")
    
    def display_contacts(self, contacts):
        """Отображение контактов в табличном формате"""
        if not contacts:
            print("No contacts to display")
            return
        
        print("\n" + "="*120)
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Group':<12} {'Phones':<50}")
        print("="*120)
        
        for contact in contacts:
            contact_id = contact[0]
            name = contact[1]
            email = contact[2] if len(contact) > 2 else ''
            group = contact[4] if len(contact) > 4 else ''
            phones = contact[5] if len(contact) > 5 else ''
            
            print(f"{contact_id:<5} {name:<20} {str(email)[:30]:<30} {str(group):<12} {str(phones)[:50]:<50}")
        print("="*120 + "\n")
    
    def console_loop(self):
        """Главный цикл консольного интерфейса"""
        print("\n" + "="*50)
        print("PHONEBOOK APPLICATION")
        print("="*50)
        
        while True:
            print("\nAvailable commands:")
            print("1. Show all contacts")
            print("2. Add contact")
            print("3. Add phone number")
            print("4. Filter by group")
            print("5. Search by email")
            print("6. Search all fields")
            print("7. Move to group")
            print("8. Sort contacts")
            print("9. Pagination")
            print("10. Export to JSON")
            print("11. Import from JSON")
            print("12. Import from CSV")
            print("13. Exit")
            
            choice = input("\nSelect action: ")
            
            if choice == '1':
                contacts = self.get_sorted_contacts()
                self.display_contacts(contacts)
            
            elif choice == '2':
                name = input("Name: ")
                email = input("Email: ")
                birthday = input("Birthday (YYYY-MM-DD): ")
                print("Available groups: Family, Work, Friend, Other")
                group = input("Group: ") or 'Other'
                self.add_contact(name, email or None, birthday or None, group)
            
            elif choice == '3':
                name = input("Contact name: ")
                phone = input("Phone number: ")
                phone_type = input("Type (home/work/mobile): ")
                self.add_phone(name, phone, phone_type)
            
            elif choice == '4':
                group = input("Group name to filter: ")
                contacts = self.filter_by_group(group)
                self.display_contacts(contacts)
            
            elif choice == '5':
                pattern = input("Email pattern to search: ")
                contacts = self.search_by_email(pattern)
                self.display_contacts(contacts)
            
            elif choice == '6':
                query = input("Search query: ")
                contacts = self.search_contacts(query)
                self.display_contacts(contacts)
            
            elif choice == '7':
                name = input("Contact name: ")
                group = input("New group name: ")
                self.move_to_group(name, group)
            
            elif choice == '8':
                print("Sort by: name, birthday, date_added")
                sort = input("Choose: ")
                if sort in ['name', 'birthday', 'date_added']:
                    contacts = self.get_sorted_contacts(sort)
                    self.display_contacts(contacts)
                else:
                    print("Invalid sort option")
            
            elif choice == '9':
                page = int(input("Page number: "))
                contacts = self.paginate(page)
                self.display_contacts(contacts)
                print(f"Page {page} (showing {self.page_size} contacts per page)")
            
            elif choice == '10':
                filename = input("Filename (default contacts_export.json): ") or 'contacts_export.json'
                self.export_to_json(filename)
            
            elif choice == '11':
                filename = input("Filename (default contacts_export.json): ") or 'contacts_export.json'
                self.import_from_json(filename)
            
            elif choice == '12':
                filename = input("Filename (default contacts.csv): ") or 'contacts.csv'
                self.import_from_csv(filename)
            
            elif choice == '13':
                print("Goodbye!")
                if self.conn:
                    self.conn.close()
                break
            
            else:
                print("Invalid command. Please try again.")

def main():
    """Главная функция запуска приложения"""
    pb = PhoneBook()
    
    if not pb.conn:
        print("Failed to connect to database. Please check your config.py")
        return
    
    # Инициализация БД при первом запуске
    choice = input("Initialize database? (y/n): ")
    if choice.lower() == 'y':
        pb.init_db()
    
    pb.console_loop()

if __name__ == "__main__":
    main()