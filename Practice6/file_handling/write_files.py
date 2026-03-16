with open("sample.txt", "w") as file:
    file.write("Apple\n")
    file.write("Banana\n")
    file.write("Orange\n")

with open("sample.txt", "a") as file:
    file.write("Mango\n")
    file.write("Grapes\n")

print("Data written and appended successfully.")