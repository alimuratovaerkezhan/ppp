# phonebook.py
import psycopg2
import csv
from config import load_config
from connect import get_connection, execute_query, execute_procedure, execute_function

def setup_database():
    """Создает таблицу, функции и процедуры в базе данных"""
    print("\n--- Setting up database ---")
    conn = get_connection()
    if conn is None:
        return
    
    cur = conn.cursor()
    try:
        # Создаем таблицу если не существует
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                phone_number VARCHAR(20) NOT NULL UNIQUE
            )
        """)
        
        # Удаляем старые функции и процедуры
        print("📦 Dropping existing functions and procedures...")
        
        # Удаляем функции
        cur.execute("DROP FUNCTION IF EXISTS search_contacts_by_pattern(TEXT)")
        cur.execute("DROP FUNCTION IF EXISTS get_contacts_paginated(INTEGER, INTEGER)")
        cur.execute("DROP FUNCTION IF EXISTS is_valid_phone(VARCHAR)")
        cur.execute("DROP FUNCTION IF EXISTS get_phonebook_stats()")
        
        # Удаляем процедуры
        cur.execute("DROP PROCEDURE IF EXISTS upsert_contact(VARCHAR, VARCHAR)")
        cur.execute("DROP PROCEDURE IF EXISTS insert_multiple_contacts(TEXT[][])")
        cur.execute("DROP PROCEDURE IF EXISTS delete_contact_by_identifier(VARCHAR)")
        cur.execute("DROP PROCEDURE IF EXISTS cleanup_invalid_phones()")
        
        conn.commit()
        print("✅ Old functions and procedures removed")
        
        # Выполняем functions.sql
        print("📦 Creating functions...")
        with open('functions.sql', 'r') as f:
            cur.execute(f.read())
        
        # Выполняем procedures.sql
        print("📦 Creating procedures...")
        with open('procedures.sql', 'r') as f:
            cur.execute(f.read())
        
        conn.commit()
        print("✅ Database setup completed successfully!")
    except Exception as error:
        conn.rollback()
        print(f"❌ Error setting up database: {error}")
    finally:
        cur.close()
        conn.close()

def show_all_contacts():
    """Показывает все контакты"""
    print("\n--- All Contacts ---")
    results = execute_query(
        "SELECT id, first_name, phone_number FROM phonebook ORDER BY first_name",
        fetch_all=True
    )
    
    if results:
        print("-" * 60)
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
        print("-" * 60)
        print(f"Total: {len(results)} contacts")
    else:
        print("📭 Phone book is empty.")

def search_contacts():
    """Поиск контактов через функцию БД"""
    print("\n--- Search Contacts (Database Function) ---")
    pattern = input("Enter search pattern (name or phone): ").strip()
    
    if not pattern:
        print("Search pattern cannot be empty.")
        return
    
    results = execute_function('search_contacts_by_pattern', (pattern,))
    
    if results:
        print(f"\n✅ Found {len(results)} contact(s):")
        print("-" * 60)
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
        print("-" * 60)
    else:
        print("❌ No contacts found.")

def paginated_contacts():
    """Пагинация через функцию БД"""
    print("\n--- Paginated Contacts ---")
    
    try:
        page = int(input("Enter page number (starting from 1): ").strip())
        per_page = int(input("Enter contacts per page (e.g., 3): ").strip())
    except ValueError:
        print("Please enter valid numbers.")
        return
    
    if page < 1 or per_page < 1:
        print("Page number and rows per page must be positive.")
        return
    
    results = execute_function('get_contacts_paginated', (page, per_page))
    
    if results:
        total_count = results[0][3] if results else 0
        print(f"\n📄 Page {page} (showing {len(results)} of {total_count} total contacts):")
        print("-" * 60)
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
        print("-" * 60)
        
        total_pages = (total_count + per_page - 1) // per_page
        print(f"📊 Page {page} of {total_pages}")
    else:
        print("❌ No contacts found on this page.")

def upsert_contact():
    """Добавление или обновление контакта через процедуру"""
    print("\n--- Upsert Contact (Insert or Update) ---")
    name = input("Enter contact name: ").strip()
    phone = input("Enter phone number: ").strip()
    
    if not name or not phone:
        print("Name and phone cannot be empty.")
        return
    
    result = execute_procedure('upsert_contact', (name, phone))
    if result is not None:
        print(f"✅ Operation completed successfully!")

def batch_insert_contacts():
    """Массовая вставка контактов через процедуру"""
    print("\n--- Batch Insert Contacts ---")
    print("Options:")
    print("1. Import from CSV file")
    print("2. Enter manually")
    choice = input("Your choice (1 or 2): ").strip()
    
    contacts_array = []
    
    if choice == '1':
        filename = input("Enter CSV filename (e.g., 'contacts.csv'): ").strip()
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 2 and row[0] and row[1]:
                        contacts_array.append([row[0].strip(), row[1].strip()])
            print(f"📁 Loaded {len(contacts_array)} contacts from {filename}")
        except FileNotFoundError:
            print(f"❌ File '{filename}' not found.")
            return
    elif choice == '2':
        print("Enter contacts (name,phone). Enter empty line to finish:")
        while True:
            line = input("Name,Phone: ").strip()
            if not line:
                break
            parts = line.split(',')
            if len(parts) >= 2:
                contacts_array.append([parts[0].strip(), parts[1].strip()])
            else:
                print("Invalid format. Use: Name,Phone")
    else:
        print("Invalid choice.")
        return
    
    if not contacts_array:
        print("No contacts to insert.")
        return
    
    result = execute_procedure('insert_multiple_contacts', (contacts_array,))
    if result is not None:
        print(f"✅ Batch insert completed!")

def delete_contact():
    """Удаление контакта через процедуру"""
    print("\n--- Delete Contact ---")
    identifier = input("Enter name or phone number to delete: ").strip()
    
    if not identifier:
        print("Identifier cannot be empty.")
        return
    
    result = execute_procedure('delete_contact_by_identifier', (identifier,))
    if result is not None:
        print(f"✅ Delete operation completed!")

def show_statistics():
    """Показывает статистику через функцию БД"""
    print("\n--- PhoneBook Statistics ---")
    results = execute_function('get_phonebook_stats')
    
    if results:
        print("-" * 40)
        print(f"📊 Total contacts: {results[0][0]}")
        print(f"📊 Unique phone numbers: {results[0][1]}")
        print("-" * 40)

def main_menu():
    """Главное меню"""
    while True:
        print("\n" + "="*50)
        print("     PHONE BOOK WITH STORED PROCEDURES")
        print("="*50)
        print("1. Show all contacts")
        print("2. Search contacts (database function)")
        print("3. Paginated contacts (database function)")
        print("4. Upsert contact - Insert or Update (stored procedure)")
        print("5. Batch insert multiple contacts (stored procedure)")
        print("6. Delete contact (stored procedure)")
        print("7. Show phonebook statistics")
        print("0. Exit")
        print("-"*50)
        
        choice = input("Select action: ").strip()
        
        if choice == '1':
            show_all_contacts()
        elif choice == '2':
            search_contacts()
        elif choice == '3':
            paginated_contacts()
        elif choice == '4':
            upsert_contact()
        elif choice == '5':
            batch_insert_contacts()
        elif choice == '6':
            delete_contact()
        elif choice == '7':
            show_statistics()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    print("\n🚀 PHONE BOOK WITH POSTGRESQL FUNCTIONS & PROCEDURES")
    print("="*50)
    
    # Настройка базы данных
    setup_database()
    
    # Запуск главного меню
    main_menu()