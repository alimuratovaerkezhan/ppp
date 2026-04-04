-- procedures.sql
-- Все хранимые процедуры для телефонной книги

-- Удаляем старые процедуры, если они существуют
DROP PROCEDURE IF EXISTS upsert_contact(VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS insert_multiple_contacts(TEXT[][]);
DROP PROCEDURE IF EXISTS delete_contact_by_identifier(VARCHAR);
DROP PROCEDURE IF EXISTS cleanup_invalid_phones();

-- 1. Процедура: добавить или обновить контакт (upsert)
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT is_valid_phone(p_phone) THEN
        RAISE EXCEPTION 'Invalid phone number format: %', p_phone;
    END IF;
    
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_name) THEN
        UPDATE phonebook 
        SET phone_number = p_phone 
        WHERE first_name = p_name;
        
        RAISE NOTICE 'Contact "%" updated with new phone: %', p_name, p_phone;
    ELSE
        INSERT INTO phonebook (first_name, phone_number)
        VALUES (p_name, p_phone);
        
        RAISE NOTICE 'New contact "%" added with phone: %', p_name, p_phone;
    END IF;
END;
$$;

-- 2. Процедура: массовая вставка контактов с валидацией
CREATE OR REPLACE PROCEDURE insert_multiple_contacts(
    contacts_data TEXT[][]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER;
    contact_name VARCHAR;
    contact_phone VARCHAR;
    invalid_count INTEGER := 0;
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS invalid_contacts (
        name VARCHAR,
        phone VARCHAR,
        error_reason VARCHAR
    ) ON COMMIT DROP;
    
    DELETE FROM invalid_contacts;
    
    FOR i IN 1..array_length(contacts_data, 1) LOOP
        contact_name := contacts_data[i][1];
        contact_phone := contacts_data[i][2];
        
        IF contact_name IS NULL OR contact_name = '' THEN
            INSERT INTO invalid_contacts VALUES (contact_name, contact_phone, 'Name cannot be empty');
            invalid_count := invalid_count + 1;
        ELSIF NOT is_valid_phone(contact_phone) THEN
            INSERT INTO invalid_contacts VALUES (contact_name, contact_phone, 'Invalid phone number format');
            invalid_count := invalid_count + 1;
        ELSE
            BEGIN
                INSERT INTO phonebook (first_name, phone_number)
                VALUES (contact_name, contact_phone);
            EXCEPTION WHEN unique_violation THEN
                UPDATE phonebook 
                SET first_name = contact_name 
                WHERE phone_number = contact_phone;
                RAISE NOTICE 'Contact with phone % updated to name %', contact_phone, contact_name;
            END;
        END IF;
    END LOOP;
    
    IF invalid_count > 0 THEN
        RAISE NOTICE 'Invalid contacts found: %', invalid_count;
    ELSE
        RAISE NOTICE 'All contacts inserted successfully!';
    END IF;
END;
$$;

-- 3. Процедура: удаление контакта по имени или телефону
CREATE OR REPLACE PROCEDURE delete_contact_by_identifier(
    identifier VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM phonebook
        WHERE first_name = identifier OR phone_number = identifier
        RETURNING *
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    IF deleted_count > 0 THEN
        RAISE NOTICE 'Successfully deleted % contact(s) matching "%"', deleted_count, identifier;
    ELSE
        RAISE NOTICE 'No contact found matching "%"', identifier;
    END IF;
END;
$$;

-- 4. Процедура: очистка невалидных номеров
CREATE OR REPLACE PROCEDURE cleanup_invalid_phones()
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM phonebook
    WHERE NOT is_valid_phone(phone_number)
    RETURNING COUNT(*) INTO deleted_count;
    
    RAISE NOTICE 'Deleted % contacts with invalid phone numbers', deleted_count;
END;
$$;