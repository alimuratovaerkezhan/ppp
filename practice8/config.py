# config.py
def load_config():
    """Загружает конфигурацию для подключения к PostgreSQL"""
    return {
        'host': 'localhost',
        'database': 'phonebook_db',
        'user': 'postgres',
        'password': 'postgres',  # Используйте ваш пароль
        'port': 5432
    }