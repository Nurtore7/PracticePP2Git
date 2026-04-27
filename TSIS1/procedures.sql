-- Процедура добавления телефона существующему контакту
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Получаем ID контакта
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    
    -- Добавляем телефон
    INSERT INTO phones (contact_id, phone, type) 
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;

-- Процедура перемещения контакта в группу
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
    v_contact_id INTEGER;
BEGIN
    -- Получаем ID контакта
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    
    -- Проверяем существование группы, если нет - создаем
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;
    
    -- Обновляем группу контакта
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

-- Функция расширенного поиска
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        STRING_AGG(DISTINCT p.phone || ' (' || p.type || ')', ', ') AS phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE 
        c.name ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY c.name;
END;
$$;

-- Функция пагинации (из Practice 8, но обновленная)
CREATE OR REPLACE FUNCTION get_paginated_contacts(
    p_limit INTEGER,
    p_offset INTEGER,
    p_sort_by VARCHAR DEFAULT 'name'
)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        STRING_AGG(p.phone || ' (' || p.type || ')', ', ') AS phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY 
        CASE WHEN p_sort_by = 'name' THEN c.name END,
        CASE WHEN p_sort_by = 'birthday' THEN c.birthday END,
        CASE WHEN p_sort_by = 'id' THEN c.id END
    LIMIT p_limit OFFSET p_offset;
END;
$$;