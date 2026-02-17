class Person:
  def __init__(self, name):
    self.name = name
  def greet(self):
    print("Hello, my name is " + self.name)
p1 = Person("Emil")
p1.greet()


class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age
  def celebrate_birthday(self):
    self.age += 1
    print(f"Happy birthday! You are now {self.age}")
p1 = Person("Linus", 25)
p1.celebrate_birthday()
p1.celebrate_birthday()