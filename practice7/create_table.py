import psycopg2
from config import load_config

def create_phonebook_table():
    """Создает таблицу phonebook в базе данных, если она еще не существует."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        phone_number VARCHAR(20) NOT NULL UNIQUE
    );
    """
    conn = None
    try:
        # Загружаем конфигурацию и подключаемся к БД
        config = load_config()
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        # Выполняем SQL-запрос для создания таблицы
        cur.execute(create_table_sql)
        
        # Фиксируем изменения
        conn.commit()
        cur.close()
        print("Таблица 'phonebook' успешно создана или уже существует.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при создании таблицы: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_phonebook_table()