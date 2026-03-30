from connect import get_connection
import csv

def add_contact():
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()

    name = input("Enter name: ")
    phone = input("Enter phone: ")

    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Contact added")


def show_contacts():
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_contact():
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()

    name = input("Enter name to update: ")
    new_phone = input("Enter new phone: ")

    cur.execute(
        "UPDATE phonebook SET phone = %s WHERE name = %s",
        (new_phone, name)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Updated successfully")


def delete_contact():
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()

    name = input("Enter name to delete: ")

    cur.execute(
        "DELETE FROM phonebook WHERE name = %s",
        (name,)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Deleted successfully")


def search_contact():
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()

    word = input("Search: ")

    cur.execute(
        "SELECT * FROM phonebook WHERE name ILIKE %s",
        ("%" + word + "%",)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def import_csv():
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()

    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )

    conn.commit()
    cur.close()
    conn.close()

    print("CSV imported")


# МЕНЮ
while True:
    print("\n1 - Add contact")
    print("2 - Show contacts")
    print("3 - Update contact")
    print("4 - Delete contact")
    print("5 - Search")
    print("6 - Import CSV")
    print("0 - Exit")

    choice = input("Choose: ")

    if choice == "1":
        add_contact()
    elif choice == "2":
        show_contacts()
    elif choice == "3":
        update_contact()
    elif choice == "4":
        delete_contact()
    elif choice == "5":
        search_contact()
    elif choice == "6":
        import_csv()
    elif choice == "0":
        break