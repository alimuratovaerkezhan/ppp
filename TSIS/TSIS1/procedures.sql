CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE username ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Phone type must be home, work, or mobile. Got: %', p_type;
    END IF;

    
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact %.', p_phone, p_type, p_contact_name;
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE username ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    
    SELECT id INTO v_group_id
    FROM groups
    WHERE name ILIKE p_group_name
    LIMIT 1;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name)
        RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created.', p_group_name;
    END IF;

    
    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id    INTEGER,
    username      VARCHAR,
    email         VARCHAR,
    birthday      DATE,
    group_name    VARCHAR,
    matched_field TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pattern TEXT := '%' || p_query || '%';
BEGIN
    
    RETURN QUERY
    SELECT c.id, c.username, c.email, c.birthday, g.name, 'username'::TEXT
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    WHERE c.username ILIKE v_pattern;

    RETURN QUERY
    SELECT c.id, c.username, c.email, c.birthday, g.name, 'email'::TEXT
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    WHERE c.email ILIKE v_pattern
      AND c.id NOT IN (
          SELECT c2.id FROM contacts c2
          WHERE c2.username ILIKE v_pattern
      );

    RETURN QUERY
    SELECT DISTINCT c.id, c.username, c.email, c.birthday, g.name, 'phone'::TEXT
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    JOIN phones p ON p.contact_id = c.id
    WHERE p.phone ILIKE v_pattern
      AND c.id NOT IN (
          SELECT c2.id FROM contacts c2
          WHERE c2.username ILIKE v_pattern
             OR c2.email    ILIKE v_pattern
      );
END;
$$;
