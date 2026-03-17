names = ["Ali", "Nurlan", "Dias"]
ages = [18, 19, 20]

print("Using enumerate():")
for index, name in enumerate(names, start=1):
    print(index, name)

print("\nUsing zip():")
for name, age in zip(names, ages):
    print(name, age)

numbers = [5, 2, 8, 1]
print("\nSorted numbers:", sorted(numbers))

x="10"
b=int(x)
print(type(b), b)