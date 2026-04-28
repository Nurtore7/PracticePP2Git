# phonebook.py
# Основное приложение телефонного справочника

# ИМПОРТ МОДУЛЕЙ
# psycopg2 - драйвер для работы с PostgreSQL
import psycopg2
# json - для экспорта/импорта данных в JSON формат
import json
# csv - для импорта данных из CSV файлов
import csv
# datetime - для работы с датами (день рождения)
from datetime import datetime
# get_connection - пользовательская функция из файла connect.py для подключения к БД
from connect import get_connection
# DB_CONFIG - словарь с параметрами подключения к БД из config.py
from config import DB_CONFIG

# ОПРЕДЕЛЕНИЕ КЛАССА ТЕЛЕФОННОГО СПРАВОЧНИКА
class PhoneBook:
    """Класс для управления телефонным справочником"""
    
    # КОНСТРУКТОР - ВЫЗЫВАЕТСЯ ПРИ СОЗДАНИИ ОБЪЕКТА
    def __init__(self):
        """Инициализация соединения с БД и параметров"""
        # Установка соединения с PostgreSQL
        self.conn = get_connection()
        # Текущая страница для пагинации (начинается с 1)
        self.current_page = 1
        # Количество контактов на одной странице
        self.page_size = 5
        # Поле для сортировки по умолчанию
        self.sort_by = 'name'
    
    # ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
    def init_db(self):
        """Инициализация базы данных - создание таблиц и процедур"""
        try:
            # Открываем курсор для выполнения SQL-запросов
            with self.conn.cursor() as cur:
                # Выполняем schema.sql (создание таблиц)
                with open('schema.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
                
                # Выполняем procedures.sql (создание хранимых процедур)
                with open('procedures.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
                
                # Фиксируем изменения в БД
                self.conn.commit()
                print("Database initialized successfully")
        except Exception as e:
            # При ошибке выводим сообщение и откатываем изменения
            print(f"Initialization error: {e}")
            self.conn.rollback()
    
    # ДОБАВЛЕНИЕ НОВОГО КОНТАКТА
    def add_contact(self, name, email=None, birthday=None, group_name='Other'):
        """Добавление нового контакта"""
        try:
            with self.conn.cursor() as cur:
                # ПОЛУЧАЕМ ID ГРУППЫ
                # Поиск группы по имени (используем %s для защиты от SQL-инъекций)
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                group = cur.fetchone()  # Получаем результат
                if not group:
                    # Группа не найдена - создаём новую
                    # RETURNING id - сразу возвращает ID созданной записи
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                    group_id = cur.fetchone()[0]  # Извлекаем ID из результата
                else:
                    # Группа существует - берём её ID
                    group_id = group[0]
                
                # ДОБАВЛЯЕМ КОНТАКТ
                # Вставка контакта с возвратом ID
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, email, birthday, group_id))
                contact_id = cur.fetchone()[0]  # Получаем ID нового контакта
                self.conn.commit()  # Фиксируем изменения
                print(f"Contact '{name}' added with ID {contact_id}")
                return contact_id  # Возвращаем ID для дальнейшего использования
        except Exception as e:
            print(f"Error adding contact: {e}")
            self.conn.rollback()  # Откат при ошибке
            return None
    
    # ДОБАВЛЕНИЕ ТЕЛЕФОНА ДЛЯ КОНТАКТА
    def add_phone(self, contact_name, phone, phone_type):
        """Добавление телефона для контакта"""
        try:
            with self.conn.cursor() as cur:
                # Находим контакт по имени
                cur.execute("SELECT id FROM contacts WHERE name = %s", (contact_name,))
                contact = cur.fetchone()
                
                if contact:
                    contact_id = contact[0]  # Берём ID контакта
                    # Добавляем телефон (без RETURNING, так как ID не нужен)
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
    
    # ПЕРЕМЕЩЕНИЕ КОНТАКТА В ДРУГУЮ ГРУППУ
    def move_to_group(self, contact_name, group_name):
        """Перемещение в группу"""
        try:
            with self.conn.cursor() as cur:
                # Находим контакт по имени
                cur.execute("SELECT id FROM contacts WHERE name = %s", (contact_name,))
                contact = cur.fetchone()
                
                if not contact:
                    print(f"Contact '{contact_name}' not found")
                    return False
                
                contact_id = contact[0]  # ID контакта
                
                # Находим или создаем группу
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                group = cur.fetchone()
                
                if not group:
                    # Создаём новую группу
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                    group_id = cur.fetchone()[0]
                    print(f"Created new group: {group_name}")
                else:
                    group_id = group[0]  # Берём ID существующей группы
                
                # Обновляем группу контакта
                cur.execute("UPDATE contacts SET group_id = %s WHERE id = %s", (group_id, contact_id))
                self.conn.commit()
                print(f"Contact '{contact_name}' moved to group '{group_name}'")
                return True
        except Exception as e:
            print(f"Error moving contact: {e}")
            self.conn.rollback()
            return False
    
    # ФИЛЬТРАЦИЯ КОНТАКТОВ ПО ГРУППЕ
    def filter_by_group(self, group_name):
        """Фильтрация контактов по группе"""
        try:
            with self.conn.cursor() as cur:
                # Сложный SQL-запрос с объединением таблиц
                # COALESCE - заменяет NULL на значение по умолчанию
                # STRING_AGG - объединяет несколько телефонов в одну строку
                # LEFT JOIN - сохраняет контакты даже без телефонов
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
                return cur.fetchall()  # Возвращаем все строки результата
        except Exception as e:
            print(f"Error filtering by group: {e}")
            return []  # Возвращаем пустой список при ошибке
    
    # ПОИСК ПО EMAIL
    def search_by_email(self, email_pattern):
        """Поиск по email с частичным совпадением"""
        try:
            with self.conn.cursor() as cur:
                # ILIKE - регистронезависимый поиск
                # % - символы-шаблоны для частичного совпадения
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
                """, (f'%{email_pattern}%',))  # Добавляем % для частичного совпадения
                return cur.fetchall()
        except Exception as e:
            print(f"Error searching by email: {e}")
            return []
    
    # РАСШИРЕННЫЙ ПОИСК ПО ВСЕМ ПОЛЯМ С РЕЛЕВАНТНОСТЬЮ
    def search_contacts(self, query):
        """Расширенный поиск по всем полям"""
        try:
            with self.conn.cursor() as cur:
                # SELECT DISTINCT - убираем дубликаты
                # CASE - вычисляем релевантность (вес совпадения)
                # Имя - 3 очка, email и телефон - 2 очка
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
                    ORDER BY relevance DESC, c.name  -- Сначала самые релевантные
                """, (f'%{query}%', f'%{query}%', f'%{query}%', 
                      f'%{query}%', f'%{query}%', f'%{query}%'))
                return cur.fetchall()
        except Exception as e:
            print(f"Error searching contacts: {e}")
            return []
    
    # ПОЛУЧЕНИЕ ОТСОРТИРОВАННЫХ КОНТАКТОВ
    def get_sorted_contacts(self, sort_by='name'):
        """Получение отсортированных контактов"""
        # Словарь соответствия полей сортировки SQL-выражениям
        # NULLS LAST - NULL значения в датах идут в конце
        order_by = {
            'name': 'c.name',
            'birthday': 'c.birthday NULLS LAST',
            'date_added': 'c.created_at'
        }.get(sort_by, 'c.name')  # По умолчанию сортировка по имени
        
        try:
            with self.conn.cursor() as cur:
                # ВНИМАНИЕ: {order_by} вставляется через f-string (потенциальная уязвимость)
                # В данном случае безопасно, так как значения берутся из словаря выше
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
    
    # ПАГИНАЦИЯ - ПОСТРАНИЧНЫЙ ВЫВОД КОНТАКТОВ
    def paginate(self, page_num):
        """Получение страницы контактов"""
        try:
            with self.conn.cursor() as cur:
                # LIMIT - максимальное количество записей
                # OFFSET - сколько записей пропустить
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
                """, (self.page_size, (page_num - 1) * self.page_size))  # Формула смещения страницы
                return cur.fetchall()
        except Exception as e:
            print(f"Error in pagination: {e}")
            return []
    
    # ЭКСПОРТ В JSON ФАЙЛ
    def export_to_json(self, filename='contacts_export.json'):
        """Экспорт всех контактов в JSON файл"""
        contacts = self.get_sorted_contacts()  # Получаем все контакты
        data = []  # Подготавливаем список для JSON
        for contact in contacts:
            # Преобразуем кортеж в словарь для читаемого JSON
            data.append({
                'id': contact[0],
                'name': contact[1],
                'email': contact[2],
                'birthday': str(contact[3]) if contact[3] else None,  # Дата в строку
                'group': contact[4],
                'phones': contact[5]
            })
        
        # Записываем JSON с отступами и поддержкой UTF-8
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)  # ensure_ascii=False для русских букв
        print(f"Exported {len(data)} contacts to {filename}")
    
    # ИМПОРТ ИЗ JSON ФАЙЛА
    def import_from_json(self, filename='contacts_export.json'):
        """Импорт контактов из JSON файла с обработкой дубликатов"""
        try:
            # Читаем JSON файл
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
                            # Удаляем существующий контакт (каскадно удалятся и телефоны)
                            cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                            self.conn.commit()
                        else:
                            continue  # Пропускаем этот контакт
                
                # Добавляем контакт (метод сам обработает создание группы)
                self.add_contact(
                    name=contact['name'],
                    email=contact.get('email'),  # .get() безопасно возвращает None, если ключа нет
                    birthday=contact.get('birthday'),
                    group_name=contact.get('group', 'Other')
                )
            print("Import completed successfully")
        except Exception as e:
            print(f"Import error: {e}")
    
    # ИМПОРТ ИЗ CSV ФАЙЛА
    def import_from_csv(self, filename='contacts.csv'):
        """Импорт контактов из CSV файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)  # Читает первую строку как заголовки
                for row in reader:
                    # Сначала добавляем контакт
                    contact_id = self.add_contact(
                        name=row['name'],  # Обязательное поле
                        email=row.get('email'),
                        birthday=row.get('birthday') if row.get('birthday') else None,
                        group_name=row.get('group', 'Other')
                    )
                    # Если контакт создан и есть телефон - добавляем телефон
                    if contact_id and row.get('phone'):
                        self.add_phone(row['name'], row['phone'], row.get('phone_type', 'mobile'))
            print("CSV import completed successfully")
        except Exception as e:
            print(f"CSV import error: {e}")
    
    # ОТОБРАЖЕНИЕ КОНТАКТОВ В ТАБЛИЧНОМ ФОРМАТЕ
    def display_contacts(self, contacts):
        """Отображение контактов в табличном формате"""
        if not contacts:
            print("No contacts to display")
            return
        
        # Форматируем вывод таблицы
        print("\n" + "="*120)
        # :<5 - выравнивание влево на 5 символов
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Group':<12} {'Phones':<50}")
        print("="*120)
        
        for contact in contacts:
            # Извлекаем данные из кортежа с проверкой длины
            contact_id = contact[0]
            name = contact[1]
            email = contact[2] if len(contact) > 2 else ''
            group = contact[4] if len(contact) > 4 else ''
            phones = contact[5] if len(contact) > 5 else ''
            
            # [:30] - обрезаем длинные строки, чтобы таблица не разрывалась
            print(f"{contact_id:<5} {name:<20} {str(email)[:30]:<30} {str(group):<12} {str(phones)[:50]:<50}")
        print("="*120 + "\n")
    
    # ГЛАВНЫЙ ЦИКЛ КОНСОЛЬНОГО ИНТЕРФЕЙСА
    def console_loop(self):
        """Главный цикл консольного интерфейса"""
        print("\n" + "="*50)
        print("PHONEBOOK APPLICATION")
        print("="*50)
        
        while True:  # Бесконечный цикл до команды Exit
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
            
            # ОБРАБОТКА КОМАНД
            if choice == '1':  # Показать все контакты
                contacts = self.get_sorted_contacts()
                self.display_contacts(contacts)
            
            elif choice == '2':  # Добавить контакт
                name = input("Name: ")
                email = input("Email: ")
                birthday = input("Birthday (YYYY-MM-DD): ")
                print("Available groups: Family, Work, Friend, Other")
                group = input("Group: ") or 'Other'  # Если пусто - ставим 'Other'
                self.add_contact(name, email or None, birthday or None, group)
            
            elif choice == '3':  # Добавить телефон
                name = input("Contact name: ")
                phone = input("Phone number: ")
                phone_type = input("Type (home/work/mobile): ")
                self.add_phone(name, phone, phone_type)
            
            elif choice == '4':  # Фильтр по группе
                group = input("Group name to filter: ")
                contacts = self.filter_by_group(group)
                self.display_contacts(contacts)
            
            elif choice == '5':  # Поиск по email
                pattern = input("Email pattern to search: ")
                contacts = self.search_by_email(pattern)
                self.display_contacts(contacts)
            
            elif choice == '6':  # Расширенный поиск
                query = input("Search query: ")
                contacts = self.search_contacts(query)
                self.display_contacts(contacts)
            
            elif choice == '7':  # Переместить в группу
                name = input("Contact name: ")
                group = input("New group name: ")
                self.move_to_group(name, group)
            
            elif choice == '8':  # Сортировка
                print("Sort by: name, birthday, date_added")
                sort = input("Choose: ")
                if sort in ['name', 'birthday', 'date_added']:  # Валидация ввода
                    contacts = self.get_sorted_contacts(sort)
                    self.display_contacts(contacts)
                else:
                    print("Invalid sort option")
            
            elif choice == '9':  # Пагинация
                page = int(input("Page number: "))  # Преобразуем строку в число
                contacts = self.paginate(page)
                self.display_contacts(contacts)
                print(f"Page {page} (showing {self.page_size} contacts per page)")
            
            elif choice == '10':  # Экспорт JSON
                filename = input("Filename (default contacts_export.json): ") or 'contacts_export.json'
                self.export_to_json(filename)
            
            elif choice == '11':  # Импорт JSON
                filename = input("Filename (default contacts_export.json): ") or 'contacts_export.json'
                self.import_from_json(filename)
            
            elif choice == '12':  # Импорт CSV
                filename = input("Filename (default contacts.csv): ") or 'contacts.csv'
                self.import_from_csv(filename)
            
            elif choice == '13':  # Выход
                print("Goodbye!")
                if self.conn:
                    self.conn.close()  # Закрываем соединение с БД
                break  # Выход из бесконечного цикла
            
            else:  # Неизвестная команда
                print("Invalid command. Please try again.")

# ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА
def main():
    """Главная функция запуска приложения"""
    pb = PhoneBook()  # Создаём экземпляр приложения
    
    if not pb.conn:  # Проверяем подключение к БД
        print("Failed to connect to database. Please check your config.py")
        return
    
    # Инициализация БД при первом запуске
    choice = input("Initialize database? (y/n): ")
    if choice.lower() == 'y':  # .lower() - приводим к нижнему регистру
        pb.init_db()
    
    pb.console_loop()  # Запускаем главный цикл

# ТОЧКА ВХОДА В ПРОГРАММУ
# __name__ == '__main__' - проверка, что скрипт запущен напрямую, а не импортирован
if __name__ == "__main__":
    main()