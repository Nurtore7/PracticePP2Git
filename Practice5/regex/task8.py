import re

s = input()

result = re.findall(r'[A-Z][a-z]*', s)

print(result)