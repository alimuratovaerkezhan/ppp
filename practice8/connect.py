# connect.py
import psycopg2
from config import load_config

def get_connection():
    """Возвращает соединение с базой данных"""
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database connection error: {error}")
        return None

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Выполняет SQL запрос и возвращает результат"""
    conn = get_connection()
    if conn is None:
        return None
    
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            result = None
            conn.commit()
        
        return result
    except Exception as error:
        conn.rollback()
        print(f"Query execution error: {error}")
        return None
    finally:
        cur.close()
        conn.close()

def execute_procedure(proc_name, params=None):
    """Вызывает хранимую процедуру"""
    conn = get_connection()
    if conn is None:
        return None
    
    cur = conn.cursor()
    try:
        if params:
            cur.callproc(proc_name, params)
        else:
            cur.callproc(proc_name)
        
        conn.commit()
        result = cur.fetchall() if cur.description else None
        return result
    except Exception as error:
        conn.rollback()
        print(f"Procedure execution error: {error}")
        return None
    finally:
        cur.close()
        conn.close()

def execute_function(func_name, params=None):
    """Вызывает функцию PostgreSQL"""
    conn = get_connection()
    if conn is None:
        return None
    
    cur = conn.cursor()
    try:
        if params:
            cur.callproc(func_name, params)
        else:
            cur.callproc(func_name)
        
        result = cur.fetchall()
        return result
    except Exception as error:
        print(f"Function execution error: {error}")
        return None
    finally:
        cur.close()
        conn.close()