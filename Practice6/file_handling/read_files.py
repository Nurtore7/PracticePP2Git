with open("sample.txt", "r") as file:
    print("Using read():")
    print(file.read())

with open("sample.txt", "r") as file:
    print("Using readline():")
    print(file.readline().strip())

with open("sample.txt", "r") as file:
    print("Using readlines():")
    print(file.readlines())