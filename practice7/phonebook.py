import psycopg2
from psycopg2 import sql
import csv
from config import load_config

def connect_to_db():
    """Устанавливает и возвращает соединение с базой данных."""
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка подключения к базе данных: {error}")
        return None

def insert_contact_from_console():
    """
    Задание: Реализовать вставку данных, введенных с консоли (имя пользователя, телефон).
    """
    print("\n--- Добавление нового контакта (из консоли) ---")
    first_name = input("Введите имя: ").strip()
    phone_number = input("Введите номер телефона: ").strip()

    if not first_name or not phone_number:
        print("Ошибка: Имя и номер телефона не могут быть пустыми.")
        return

    conn = connect_to_db()
    if conn is None:
        return
    
    cur = conn.cursor()
    try:
        # Используем SQL запрос с плейсхолдерами для защиты от SQL-инъекций
        insert_query = """
            INSERT INTO phonebook (first_name, phone_number)
            VALUES (%s, %s)
        """
        cur.execute(insert_query, (first_name, phone_number))
        conn.commit()
        print(f"Контакт '{first_name}' успешно добавлен!")
    except psycopg2.IntegrityError:
        conn.rollback()
        print(f"Ошибка: Контакт с номером '{phone_number}' уже существует.")
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        print(f"Произошла ошибка при добавлении контакта: {error}")
    finally:
        cur.close()
        conn.close()

def insert_contacts_from_csv(csv_file_path):
    """
    Задание: Реализовать вставку данных из CSV-файла.
    """
    print(f"\n--- Импорт контактов из CSV-файла: {csv_file_path} ---")
    conn = connect_to_db()
    if conn is None:
        return

    cur = conn.cursor()
    contacts_added = 0
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Пропускаем заголовок, если он есть (например: "first_name,phone_number")
            # next(reader, None) 
            for row in reader:
                # Ожидаем формат: Имя,Телефон
                if len(row) != 2 or not row[0] or not row[1]:
                    print(f"Пропуск некорректной строки: {row}")
                    continue
                
                first_name, phone_number = row[0].strip(), row[1].strip()
                try:
                    insert_query = """
                        INSERT INTO phonebook (first_name, phone_number)
                        VALUES (%s, %s)
                    """
                    cur.execute(insert_query, (first_name, phone_number))
                    contacts_added += 1
                except psycopg2.IntegrityError:
                    # Откатываем только текущую вставку, если номер не уникален
                    conn.rollback()
                    print(f"Контакт с номером '{phone_number}' уже существует. Импорт пропущен.")
                except Exception as e:
                    conn.rollback()
                    print(f"Ошибка при вставке строки {row}: {e}")
        conn.commit()
        print(f"Импорт завершен. Успешно добавлено контактов: {contacts_added}")
    except FileNotFoundError:
        print(f"Ошибка: Файл '{csv_file_path}' не найден.")
    except Exception as error:
        print(f"Произошла ошибка при чтении CSV файла: {error}")
    finally:
        cur.close()
        conn.close()

def update_contact():
    """
    Задание: Реализовать обновление имени контакта или номера телефона.
    """
    print("\n--- Обновление информации о контакте ---")
    identifier = input("Введите имя или номер телефона контакта, который хотите обновить: ").strip()
    
    if not identifier:
        print("Ошибка: Не введены данные для поиска.")
        return
        
    conn = connect_to_db()
    if conn is None:
        return
    
    cur = conn.cursor()
    
    # Сначала найдем контакт, чтобы убедиться, что он существует
    search_query = """
        SELECT id, first_name, phone_number FROM phonebook 
        WHERE first_name = %s OR phone_number = %s
    """
    cur.execute(search_query, (identifier, identifier))
    contact = cur.fetchone()
    
    if not contact:
        print(f"Контакт с именем или номером '{identifier}' не найден.")
        cur.close()
        conn.close()
        return
        
    contact_id, current_name, current_phone = contact
    print(f"Найден контакт: Имя = '{current_name}', Телефон = '{current_phone}'")
    
    print("Что вы хотите обновить?")
    print("1. Имя")
    print("2. Номер телефона")
    choice = input("Ваш выбор (1 или 2): ").strip()
    
    update_query = None
    new_value = None
    query_param = None
    
    if choice == '1':
        new_name = input("Введите новое имя: ").strip()
        if new_name:
            update_query = "UPDATE phonebook SET first_name = %s WHERE id = %s"
            new_value = new_name
            query_param = contact_id
        else:
            print("Имя не может быть пустым.")
    elif choice == '2':
        new_phone = input("Введите новый номер телефона: ").strip()
        if new_phone:
            update_query = "UPDATE phonebook SET phone_number = %s WHERE id = %s"
            new_value = new_phone
            query_param = contact_id
        else:
            print("Номер телефона не может быть пустым.")
    else:
        print("Неверный выбор.")
        
    if update_query:
        try:
            cur.execute(update_query, (new_value, query_param))
            conn.commit()
            print("Информация о контакте успешно обновлена!")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f"Ошибка: Номер телефона '{new_phone}' уже используется другим контактом.")
        except Exception as error:
            conn.rollback()
            print(f"Ошибка при обновлении: {error}")
    
    cur.close()
    conn.close()

def query_contacts():
    """
    Задание: Реализовать запрос контактов с разными фильтрами (например, по имени, по префиксу номера).
    """
    print("\n--- Поиск контактов ---")
    print("1. Поиск по имени (полное совпадение)")
    print("2. Поиск по части имени (ILIKE)")
    print("3. Поиск по номеру телефона (полное совпадение)")
    print("4. Поиск по префиксу номера")
    choice = input("Выберите тип поиска (1-4): ").strip()
    
    search_query = None
    search_param = None
    
    if choice == '1':
        name = input("Введите имя для поиска: ").strip()
        if name:
            search_query = "SELECT * FROM phonebook WHERE first_name = %s ORDER BY first_name"
            search_param = (name,)
    elif choice == '2':
        name_part = input("Введите часть имени для поиска: ").strip()
        if name_part:
            search_query = "SELECT * FROM phonebook WHERE first_name ILIKE %s ORDER BY first_name"
            search_param = (f'%{name_part}%',)
    elif choice == '3':
        phone = input("Введите номер телефона для поиска: ").strip()
        if phone:
            search_query = "SELECT * FROM phonebook WHERE phone_number = %s"
            search_param = (phone,)
    elif choice == '4':
        prefix = input("Введите префикс номера телефона (например, '8707'): ").strip()
        if prefix:
            search_query = "SELECT * FROM phonebook WHERE phone_number LIKE %s ORDER BY phone_number"
            search_param = (f'{prefix}%',)
    else:
        print("Неверный выбор.")
        return
        
    if not search_query:
        print("Поисковый запрос не может быть пустым.")
        return

    conn = connect_to_db()
    if conn is None:
        return
        
    cur = conn.cursor()
    try:
        cur.execute(search_query, search_param)
        results = cur.fetchall()
        
        if results:
            print("\nРезультаты поиска:")
            print("-" * 50)
            for row in results:
                print(f"ID: {row[0]}, Имя: {row[1]}, Телефон: {row[2]}")
            print("-" * 50)
        else:
            print("Контакты по вашему запросу не найдены.")
    except Exception as error:
        print(f"Ошибка при выполнении поиска: {error}")
    finally:
        cur.close()
        conn.close()

def delete_contact():
    """
    Задание: Реализовать удаление контакта по имени пользователя или номеру телефона.
    """
    print("\n--- Удаление контакта ---")
    identifier = input("Введите имя или номер телефона контакта для удаления: ").strip()
    
    if not identifier:
        print("Ошибка: Не введены данные для поиска.")
        return

    conn = connect_to_db()
    if conn is None:
        return
    
    cur = conn.cursor()
    
    # Сначала найдем контакт для подтверждения
    search_query = """
        SELECT id, first_name, phone_number FROM phonebook 
        WHERE first_name = %s OR phone_number = %s
    """
    cur.execute(search_query, (identifier, identifier))
    contact = cur.fetchone()
    
    if not contact:
        print(f"Контакт с именем или номером '{identifier}' не найден.")
        cur.close()
        conn.close()
        return
        
    contact_id, contact_name, contact_phone = contact
    print(f"Вы собираетесь удалить контакт: Имя = '{contact_name}', Телефон = '{contact_phone}'")
    confirm = input("Вы уверены? (y/n): ").strip().lower()
    
    if confirm == 'y':
        try:
            delete_query = "DELETE FROM phonebook WHERE id = %s"
            cur.execute(delete_query, (contact_id,))
            conn.commit()
            print(f"Контакт '{contact_name}' успешно удален.")
        except Exception as error:
            conn.rollback()
            print(f"Ошибка при удалении: {error}")
    else:
        print("Удаление отменено.")
        
    cur.close()
    conn.close()

def show_all_contacts():
    """Показывает все контакты из телефонной книги."""
    print("\n--- Все контакты в телефонной книге ---")
    conn = connect_to_db()
    if conn is None:
        return
        
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM phonebook ORDER BY first_name")
        results = cur.fetchall()
        
        if results:
            print("-" * 50)
            for row in results:
                print(f"ID: {row[0]}, Имя: {row[1]}, Телефон: {row[2]}")
            print("-" * 50)
        else:
            print("Телефонная книга пуста.")
    except Exception as error:
        print(f"Ошибка при получении контактов: {error}")
    finally:
        cur.close()
        conn.close()

def main_menu():
    """Главное меню приложения."""
    while True:
        print("\n" + "="*30)
        print("     ТЕЛЕФОННАЯ КНИГА")
        print("="*30)
        print("1. Показать все контакты")
        print("2. Добавить контакт (из консоли)")
        print("3. Импорт контактов из CSV")
        print("4. Поиск контактов")
        print("5. Обновить контакт")
        print("6. Удалить контакт")
        print("0. Выход")
        print("-"*30)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '1':
            show_all_contacts()
        elif choice == '2':
            insert_contact_from_console()
        elif choice == '3':
            # Укажите путь к вашему CSV файлу
            csv_path = input("Введите путь к CSV файлу (например, 'contacts.csv'): ").strip()
            if csv_path:
                insert_contacts_from_csv(csv_path)
            else:
                print("Путь к файлу не может быть пустым.")
        elif choice == '4':
            query_contacts()
        elif choice == '5':
            update_contact()
        elif choice == '6':
            delete_contact()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

if __name__ == '__main__':
    # Убедимся, что таблица существует перед запуском основного меню
    # Импортируем функцию из первого шага
    # create_phonebook_table() 
    main_menu()