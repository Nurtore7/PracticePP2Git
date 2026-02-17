class Animal:
    def __init__(self, name):
        self.name = name


class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)  # вызываем конструктор родителя


d = Dog("Rex")
print(d.name)
