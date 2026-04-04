# config.py
import psycopg2
from psycopg2 import OperationalError

def load_config():
    """Загружает конфигурацию для подключения к PostgreSQL"""
    return {
        'host': 'localhost',      # или '127.0.0.1'
        'database': 'phonebook_db',  # имя вашей базы данных
        'user': 'postgres',       # ваше имя пользователя
        'password': 'postgres',   # ваш пароль (скорее всего 'postgres' или другой)
        'port': 5432              # порт PostgreSQL по умолчанию
    }

def test_connection():
    """Тестирует подключение к базе данных"""
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        print("✅ Подключение к базе данных успешно!")
        conn.close()
        return True
    except OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("\nВозможные причины:")
        print("1. PostgreSQL не запущен")
        print("2. Неправильный пароль")
        print("3. База данных не создана")
        print("4. Неправильное имя пользователя")
        return False

if __name__ == '__main__':
    test_connection()