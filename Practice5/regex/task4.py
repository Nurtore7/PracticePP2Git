import re

s = input()

if re.fullmatch("[A-Z][a-z]+", s):
    print("True")
else:
    print("False")