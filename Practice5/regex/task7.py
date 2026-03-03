s = input()

parts = s.split("_")

camel = parts[0]

for word in parts[1:]:
    camel += word.capitalize()

print(camel)