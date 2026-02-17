class Car:
    wheels = 4   # переменная класса

    def __init__(self, name):
        self.name = name


car1 = Car("BMW")
car2 = Car("Audi")

print(car1.name)
print(car2.name)

print(car1.wheels)
print(car2.wheels)
