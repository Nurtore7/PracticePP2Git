def squares(n):
    for i in range(n + 1):
        yield i * i

n = int(input())
for value in squares(n):
    print(value)