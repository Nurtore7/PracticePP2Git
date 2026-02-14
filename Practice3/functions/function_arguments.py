def my_function(fname):
  print(fname + " Refsnes")
my_function("Emil")
my_function("Tobias")
my_function("Linus")


def my_function(name): # name is a parameter
  print("Hello", name)
my_function("Emil") # "Emil" is an argument


def my_function(fname, lname):
  print(fname + " " + lname)
my_function("Emil", "Refsnes")


def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)
my_function(animal = "dog", name = "Buddy")