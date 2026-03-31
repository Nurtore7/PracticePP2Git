from connect import connect

conn = connect()
cur = conn.cursor()

while True:
    print("\n1. Add/Update")
    print("2. Search")
    print("3. Show contacts")
    print("4. Delete")
    print("5. Exit")

    choice = input("Choose: ")

    if choice == "1":
        name = input("Name: ")
        phone = input("Phone: ")
        cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()

    elif choice == "2":
        pattern = input("Search: ")
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        print(cur.fetchall())

    elif choice == "3":
        cur.execute("SELECT * FROM get_contacts(%s, %s)", (5, 0))
        print(cur.fetchall())

    elif choice == "4":
        value = input("Delete (name/phone): ")
        cur.execute("CALL delete_contact(%s)", (value,))
        conn.commit()

    elif choice == "5":
        break

cur.close()
conn.close()