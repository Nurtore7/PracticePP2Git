def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input())
result = []

for num in even_numbers(n):
    result.append(str(num))

print(",".join(result))