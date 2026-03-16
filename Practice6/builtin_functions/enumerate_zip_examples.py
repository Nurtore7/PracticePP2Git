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

x = "123"
y = "3.14"
z = 500

print("\nType conversions:")
print(int(x))
print(float(y))
print(str(z))
print(list("Python"))

print("\nType checking:")
print(type(x))
print(type(int(x)))
print(type(float(y)))
print(type(str(z)))