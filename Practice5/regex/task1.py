import re

s = input()

if re.fullmatch("ab*", s):
    print("True")
else:
    print("False")