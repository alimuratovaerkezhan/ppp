import re
# 1) 
text = input("Enter string: ")
if re.fullmatch(r"ab*", text):
    print("Match")
else:
    print("No match")


# 2) 
text = input("Enter string: ")
if re.fullmatch(r"ab{2,3}", text):
    print("Match")
else:
    print("No match")


# 3 
text = input("Enter string: ")
print(re.findall(r"[a-z]+_[a-z]+", text))


# 4
text = input("Enter string: ")
print(re.findall(r"[A-Z][a-z]+", text))


# 5 
text = input("Enter string: ")
if re.fullmatch(r"a.*b", text):
    print("Match")
else:
    print("No match")


# 6 
text = input("Enter string: ")
print(re.sub(r"[ ,\.]", ":", text))


# 7 
def snake_to_camel(s):
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

print(snake_to_camel(input("Enter snake_case string: ")))


# 8
text = input("Enter string: ")
print(re.split(r"(?=[A-Z])", text))


# 9
text = input("Enter string: ")
print(re.sub(r"(?<!^)(?=[A-Z])", " ", text))


# 10
def camel_to_snake(s):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()

print(camel_to_snake(input("Enter camelCase string: ")))