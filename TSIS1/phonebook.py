import psycopg2
import json
import csv
from datetime import datetime
from connect import get_connection, init_database

class PhoneBook:
    def __init__(self):
        self.conn = get_connection()
        if not self.conn:
            raise Exception("Не удалось подключиться к БД")
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    # ==================== 1. ФИЛЬТР ПО ГРУППЕ ====================
    def filter_by_group(self, group_name):
        """Показать контакты из выбранной группы"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.name, c.email, c.birthday, 
                           STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
                    FROM contacts c
                    LEFT JOIN phones p ON c.id = p.contact_id
                    LEFT JOIN groups g ON c.group_id = g.id
                    WHERE g.name = %s
                    GROUP BY c.id, c.name, c.email, c.birthday
                    ORDER BY c.name
                """, (group_name,))
                
                results = cur.fetchall()
                if not results:
                    print(f"Нет контактов в группе '{group_name}'")
                    return
                
                print(f"\n--- Контакты в группе '{group_name}' ---")
                for contact in results:
                    print(f"Имя: {contact[0]}")
                    print(f"Email: {contact[1] or 'Не указан'}")
                    print(f"День рождения: {contact[2] or 'Не указан'}")
                    print(f"Телефоны: {contact[3] or 'Нет'}")
                    print("-" * 30)
        except Exception as e:
            print(f"Ошибка фильтрации: {e}")
    
    # ==================== 2. ПОИСК ПО EMAIL ====================
    def search_by_email(self, email_part):
        """Поиск по части email"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.name, c.email, 
                           STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
                    FROM contacts c
                    LEFT JOIN phones p ON c.id = p.contact_id
                    WHERE c.email ILIKE %s
                    GROUP BY c.id, c.name, c.email
                    ORDER BY c.name
                """, (f'%{email_part}%',))
                
                results = cur.fetchall()
                if not results:
                    print(f"Контакты с email содержащим '{email_part}' не найдены")
                    return
                
                print(f"\n--- Контакты с email содержащим '{email_part}' ---")
                for contact in results:
                    print(f"Имя: {contact[0]}")
                    print(f"Email: {contact[1]}")
                    print(f"Телефоны: {contact[2] or 'Нет'}")
                    print("-" * 30)
        except Exception as e:
            print(f"Ошибка поиска: {e}")
    
    # ==================== 3. СОРТИРОВКА РЕЗУЛЬТАТОВ ====================
    def sort_contacts(self, sort_by):
        """Сортировка контактов"""
        valid_sort = ['name', 'birthday', 'id']
        if sort_by not in valid_sort:
            print(f"Доступные варианты: {', '.join(valid_sort)}")
            return
        
        try:
            with self.conn.cursor() as cur:
                query = f"""
                    SELECT c.name, c.email, c.birthday, 
                           STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
                    FROM contacts c
                    LEFT JOIN phones p ON c.id = p.contact_id
                    GROUP BY c.id, c.name, c.email, c.birthday
                    ORDER BY 
                        CASE WHEN %s = 'name' THEN c.name END,
                        CASE WHEN %s = 'birthday' THEN c.birthday END,
                        CASE WHEN %s = 'id' THEN c.id END
                """
                cur.execute(query, (sort_by, sort_by, sort_by))
                
                results = cur.fetchall()
                if not results:
                    print("Нет контактов в базе")
                    return
                
                print(f"\n--- Контакты (сортировка по {sort_by}) ---")
                for contact in results:
                    print(f"Имя: {contact[0]}")
                    print(f"Email: {contact[1] or 'Не указан'}")
                    print(f"День рождения: {contact[2] or 'Не указан'}")
                    print(f"Телефоны: {contact[3] or 'Нет'}")
                    print("-" * 30)
        except Exception as e:
            print(f"Ошибка сортировки: {e}")
    
    # ==================== 4. ПАГИНАЦИЯ ====================
    def paginated_view(self, limit=5):
        """Просмотр контактов с пагинацией"""
        offset = 0
        while True:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT * FROM get_paginated_contacts(%s, %s, 'name')", (limit, offset))
                    contacts = cur.fetchall()
                    
                    if not contacts:
                        print("Нет больше контактов")
                        if offset > 0:
                            offset -= limit
                        continue
                    
                    print(f"\n--- Страница {offset//limit + 1} ---")
                    for contact in contacts:
                        print(f"ID: {contact[0]}")
                        print(f"Имя: {contact[1]}")
                        print(f"Email: {contact[2] or 'Не указан'}")
                        print(f"День рождения: {contact[3] or 'Не указан'}")
                        print(f"Группа: {contact[4] or 'Без группы'}")
                        print(f"Телефоны: {contact[5] or 'Нет'}")
                        print("-" * 30)
                    
                    # Навигация
                    cmd = input("\n[next/prev/quit]: ").lower()
                    if cmd == 'next':
                        offset += limit
                    elif cmd == 'prev' and offset >= limit:
                        offset -= limit
                    elif cmd == 'quit':
                        break
                    else:
                        print("Неверная команда")
            except Exception as e:
                print(f"Ошибка: {e}")
                break
    
    # ==================== 5. ЭКСПОРТ В JSON ====================
    def export_to_json(self, filename='contacts.json'):
        """Экспорт всех контактов в JSON"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.name,
                        c.email,
                        c.birthday,
                        g.name as group_name,
                        json_agg(json_build_object('number', p.phone, 'type', p.type)) as phones
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON c.id = p.contact_id
                    GROUP BY c.id, c.name, c.email, c.birthday, g.name
                """)
                
                contacts = []
                for row in cur.fetchall():
                    contact = {
                        'name': row[0],
                        'email': row[1],
                        'birthday': str(row[2]) if row[2] else None,
                        'group': row[3],
                        'phones': row[4] if row[4] else []
                    }
                    contacts.append(contact)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(contacts, f, ensure_ascii=False, indent=2)
                
                print(f"Контакты экспортированы в {filename}")
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
    
    # ==================== 6. ИМПОРТ ИЗ JSON ====================
    def import_from_json(self, filename='contacts.json'):
        """Импорт контактов из JSON с обработкой дубликатов"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
            
            for contact in contacts:
                # Проверяем существование контакта
                with self.conn.cursor() as cur:
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (contact['name'],))
                    exists = cur.fetchone()
                    
                    if exists:
                        print(f"Контакт '{contact['name']}' уже существует")
                        choice = input("Пропустить (skip) или перезаписать (overwrite)? ").lower()
                        
                        if choice == 'skip':
                            continue
                        elif choice == 'overwrite':
                            # Удаляем старый контакт и все его телефоны
                            cur.execute("DELETE FROM contacts WHERE name = %s", (contact['name'],))
                            self.conn.commit()
                    
                    # Добавляем новый контакт
                    # Сначала получаем или создаем группу
                    group_id = None
                    if contact['group']:
                        cur.execute("SELECT id FROM groups WHERE name = %s", (contact['group'],))
                        group = cur.fetchone()
                        if group:
                            group_id = group[0]
                        else:
                            cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (contact['group'],))
                            group_id = cur.fetchone()[0]
                    
                    # Добавляем контакт
                    cur.execute("""
                        INSERT INTO contacts (name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (contact['name'], contact['email'], contact['birthday'], group_id))
                    
                    contact_id = cur.fetchone()[0]
                    
                    # Добавляем телефоны
                    for phone in contact['phones']:
                        cur.execute("""
                            INSERT INTO phones (contact_id, phone, type)
                            VALUES (%s, %s, %s)
                        """, (contact_id, phone['number'], phone['type']))
                    
                    self.conn.commit()
                    print(f"Контакт '{contact['name']}' добавлен")
            
            print("Импорт завершен")
        except Exception as e:
            print(f"Ошибка импорта: {e}")
            self.conn.rollback()
    
    # ==================== 7. РАСШИРЕННЫЙ CSV ИМПОРТ ====================
    def import_from_csv(self, filename='contacts.csv'):
        """Импорт контактов из CSV с новыми полями"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    with self.conn.cursor() as cur:
                        # Проверяем существование контакта
                        cur.execute("SELECT id FROM contacts WHERE name = %s", (row['name'],))
                        exists = cur.fetchone()
                        
                        if exists:
                            print(f"Контакт '{row['name']}' уже существует, пропускаем")
                            continue
                        
                        # Получаем или создаем группу
                        group_id = None
                        if row.get('group'):
                            cur.execute("SELECT id FROM groups WHERE name = %s", (row['group'],))
                            group = cur.fetchone()
                            if group:
                                group_id = group[0]
                            else:
                                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (row['group'],))
                                group_id = cur.fetchone()[0]
                        
                        # Добавляем контакт
                        cur.execute("""
                            INSERT INTO contacts (name, email, birthday, group_id)
                            VALUES (%s, %s, %s, %s) RETURNING id
                        """, (row['name'], row.get('email'), row.get('birthday'), group_id))
                        
                        contact_id = cur.fetchone()[0]
                        
                        # Добавляем телефоны (могут быть несколько через запятую)
                        if row.get('phones'):
                            phones = row['phones'].split(';')
                            for phone in phones:
                                parts = phone.strip().split(':')
                                if len(parts) == 2:
                                    cur.execute("""
                                        INSERT INTO phones (contact_id, phone, type)
                                        VALUES (%s, %s, %s)
                                    """, (contact_id, parts[0], parts[1]))
                        
                        self.conn.commit()
                        print(f"Контакт '{row['name']}' добавлен")
            
            print("CSV импорт завершен")
        except Exception as e:
            print(f"Ошибка CSV импорта: {e}")
            self.conn.rollback()
    
    # ==================== 8. ДОБАВЛЕНИЕ ТЕЛЕФОНА ====================
    def add_phone_to_contact(self, contact_name, phone, phone_type):
        """Добавление телефона существующему контакту (используя процедуру)"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
                self.conn.commit()
                print(f"Телефон {phone} ({phone_type}) добавлен контакту '{contact_name}'")
        except Exception as e:
            print(f"Ошибка: {e}")
            self.conn.rollback()
    
    # ==================== 9. ПЕРЕМЕЩЕНИЕ В ГРУППУ ====================
    def move_to_group(self, contact_name, group_name):
        """Перемещение контакта в группу (используя процедуру)"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
                self.conn.commit()
                print(f"Контакт '{contact_name}' перемещен в группу '{group_name}'")
        except Exception as e:
            print(f"Ошибка: {e}")
            self.conn.rollback()
    
    # ==================== 10. РАСШИРЕННЫЙ ПОИСК ====================
    def search_contacts(self, query):
        """Расширенный поиск по всем полям и телефонам"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM search_contacts(%s)", (query,))
                results = cur.fetchall()
                
                if not results:
                    print(f"Ничего не найдено по запросу '{query}'")
                    return
                
                print(f"\n--- Результаты поиска по '{query}' ---")
                for contact in results:
                    print(f"ID: {contact[0]}")
                    print(f"Имя: {contact[1]}")
                    print(f"Email: {contact[2] or 'Не указан'}")
                    print(f"День рождения: {contact[3] or 'Не указан'}")
                    print(f"Группа: {contact[4] or 'Без группы'}")
                    print(f"Телефоны: {contact[5] or 'Нет'}")
                    print("-" * 30)
        except Exception as e:
            print(f"Ошибка поиска: {e}")

# ==================== ГЛАВНОЕ МЕНЮ ====================
def main():
    # Инициализация БД
    if not init_database():
        print("Не удалось инициализировать БД")
        return
    
    pb = PhoneBook()
    
    while True:
        print("\n" + "=" * 50)
        print("📞 ТЕЛЕФОННАЯ КНИГА - РАСШИРЕННАЯ ВЕРСИЯ")
        print("=" * 50)
        print("1. Фильтр по группе")
        print("2. Поиск по email")
        print("3. Сортировка контактов")
        print("4. Просмотр с пагинацией")
        print("5. Экспорт в JSON")
        print("6. Импорт из JSON")
        print("7. Импорт из CSV (расширенный)")
        print("8. Добавить телефон контакту")
        print("9. Переместить в группу")
        print("10. Расширенный поиск")
        print("0. Выход")
        print("=" * 50)
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            group = input("Введите название группы (Family/Work/Friend/Other): ")
            pb.filter_by_group(group)
        
        elif choice == '2':
            email_part = input("Введите часть email для поиска: ")
            pb.search_by_email(email_part)
        
        elif choice == '3':
            print("Варианты сортировки: name, birthday, id")
            sort_by = input("Выберите сортировку: ")
            pb.sort_contacts(sort_by)
        
        elif choice == '4':
            limit = input("Количество записей на странице (по умолчанию 5): ")
            limit = int(limit) if limit.isdigit() else 5
            pb.paginated_view(limit)
        
        elif choice == '5':
            filename = input("Имя файла для экспорта (по умолчанию contacts.json): ")
            filename = filename if filename else 'contacts.json'
            pb.export_to_json(filename)
        
        elif choice == '6':
            filename = input("Имя файла для импорта (по умолчанию contacts.json): ")
            filename = filename if filename else 'contacts.json'
            pb.import_from_json(filename)
        
        elif choice == '7':
            filename = input("Имя CSV файла (по умолчанию contacts.csv): ")
            filename = filename if filename else 'contacts.csv'
            pb.import_from_csv(filename)
        
        elif choice == '8':
            name = input("Имя контакта: ")
            phone = input("Номер телефона: ")
            phone_type = input("Тип телефона (home/work/mobile): ")
            pb.add_phone_to_contact(name, phone, phone_type)
        
        elif choice == '9':
            name = input("Имя контакта: ")
            group = input("Название группы: ")
            pb.move_to_group(name, group)
        
        elif choice == '10':
            query = input("Введите поисковый запрос: ")
            pb.search_contacts(query)
        
        elif choice == '0':
            print("До свидания!")
            break
        
        else:
            print("Неверный выбор, попробуйте снова")
    
    pb.close()

if __name__ == "__main__":
    main()