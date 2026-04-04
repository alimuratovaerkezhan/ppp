-- functions.sql
-- Все функции для телефонной книги

-- Удаляем старые функции, если они существуют
DROP FUNCTION IF EXISTS search_contacts_by_pattern(TEXT);
DROP FUNCTION IF EXISTS get_contacts_paginated(INTEGER, INTEGER);
DROP FUNCTION IF EXISTS is_valid_phone(VARCHAR);
DROP FUNCTION IF EXISTS get_phonebook_stats();

-- 1. Функция для поиска контактов по шаблону (имя или телефон)
CREATE OR REPLACE FUNCTION search_contacts_by_pattern(search_pattern TEXT)
RETURNS TABLE(
    contact_id INTEGER,
    contact_name VARCHAR,
    contact_phone VARCHAR
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT id, first_name, phone_number
    FROM phonebook
    WHERE first_name ILIKE '%' || search_pattern || '%'
       OR phone_number ILIKE '%' || search_pattern || '%'
    ORDER BY first_name;
END;
$$;

-- 2. Функция для получения контактов с пагинацией
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    page_number INTEGER,
    rows_per_page INTEGER
)
RETURNS TABLE(
    contact_id INTEGER,
    contact_name VARCHAR,
    contact_phone VARCHAR,
    total_count BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    offset_val INTEGER;
BEGIN
    offset_val := (page_number - 1) * rows_per_page;
    
    RETURN QUERY
    SELECT 
        id,
        first_name,
        phone_number,
        COUNT(*) OVER() AS total_count
    FROM phonebook
    ORDER BY first_name
    LIMIT rows_per_page
    OFFSET offset_val;
END;
$$;

-- 3. Функция для проверки корректности номера телефона
CREATE OR REPLACE FUNCTION is_valid_phone(phone VARCHAR)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN phone ~ '^[78][0-9]{9,14}$';
END;
$$;

-- 4. Функция для получения статистики
CREATE OR REPLACE FUNCTION get_phonebook_stats()
RETURNS TABLE(
    total_contacts INTEGER,
    unique_phones INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER AS total_contacts,
        COUNT(DISTINCT phone_number)::INTEGER AS unique_phones
    FROM phonebook;
END;
$$;