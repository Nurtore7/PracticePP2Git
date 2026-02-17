def my_function(*kids):
  print("The youngest child is " + kids[2])
my_function("Emil", "Tobias", "Linus")


def my_function(greeting, *names):
  for name in names:
    print(greeting, name)
my_function("Hello", "Emil", "Tobias", "Linus")


def my_function(*numbers):
  total = 0
  for num in numbers:
    total += num
  return total
print(my_function(1, 2, 3))
print(my_function(10, 20, 30, 40))
print(my_function(5))