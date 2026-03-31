CREATE OR REPLACE FUNCTION search_contacts(p TEXT)
RETURNS TABLE(contact_name VARCHAR, contact_phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT pb.name, pb.phone
    FROM phonebook pb
    WHERE pb.name ILIKE '%' || p || '%'
       OR pb.phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT pb.id, pb.name, pb.phone
    FROM phonebook pb
    ORDER BY pb.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;