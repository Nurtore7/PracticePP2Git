# Родительский класс
class Vehicle:
    def move(self):
        print("The vehicle is moving")


# Дочерний класс
class Car(Vehicle):
    def honk(self):
        print("Beep beep!")


# Создаем объект
c = Car()
c.move()   # метод родителя
c.honk()   # метод дочернего класса
