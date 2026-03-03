import re

s = input()

if re.fullmatch("[a-z]+_[a-z]+", s):
    print("True")
else:
    print("False")