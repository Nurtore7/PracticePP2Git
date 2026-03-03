import re

s = input()

if re.fullmatch("a.*b", s):
    print("True")
else:
    print("False")