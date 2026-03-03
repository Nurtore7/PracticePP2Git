import re

s = input()

if re.fullmatch("ab{2,3}", s):
    print("True")
else:
    print("False")