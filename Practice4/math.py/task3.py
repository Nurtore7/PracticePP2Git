import math

n = int(input())
s = float(input())

area = (n * s * s) / (4 * math.tan(math.pi / n))

area = round(area)   
print(int(area))