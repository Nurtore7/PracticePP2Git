from connect import connect

import csv

def insert_console():
    conn = connect()
    cur = conn.cursor()

    name = input("Name: ")
    phone = input("Phone: ")

    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()

def show_all():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()

def insert_csv():
    conn = connect()
    cur = conn.cursor()

    with open("contacts.csv", "r") as f:
        reader = csv.reader(f)

        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )

    conn.commit()
    cur.close()
    conn.close()

def search():
    conn = connect()
    cur = conn.cursor()

    word = input("Search: ")

    cur.execute(
        "SELECT * FROM phonebook WHERE name ILIKE %s OR phone ILIKE %s",
        (f"%{word}%", f"%{word}%")
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()

def delete():
    conn = connect()
    cur = conn.cursor()

    name = input("Name to delete: ")

    cur.execute("DELETE FROM phonebook WHERE name=%s", (name,))

    conn.commit()
    cur.close()
    conn.close()

while True:
    print("\n--- PHONEBOOK MENU ---")
    print("1. Insert from CSV")
    print("2. Insert from console")
    print("3. Show all")
    print("4. Search")
    print("5. Delete")
    print("0. Exit")

    choice = input("Choose: ")

    if choice == "1":
        insert_csv()
    elif choice == "2":
        insert_console()
    elif choice == "3":
        show_all()
    elif choice == "4":
        search()
    elif choice == "5":
        delete()
    elif choice == "0":
        break