from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

squares = list(map(lambda x: x * x, numbers))
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
total = reduce(lambda a, b: a + b, numbers)

print("Numbers:", numbers)
print("Length:", len(numbers))
print("Sum:", sum(numbers))
print("Min:", min(numbers))
print("Max:", max(numbers))
print("Squares:", squares)
print("Even numbers:", even_numbers)
print("Reduce sum:", total)