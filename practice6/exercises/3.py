#Builtin func

#Use map() and filter()
numbers = [1, 2, 3, 4, 5]
# map: square numbers
squared = list(map(lambda x: x**2, numbers))
print(squared)
# filter: even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)


#Aggregate with reduce()
from functools import reduce
numbers = [1, 2, 3, 4]
sum_all = reduce(lambda x, y: x + y, numbers)
print(sum_all)



#Use enumerate() and zip()
names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 95]
# enumerate
for index, name in enumerate(names):
    print(index, name)
# zip
for name, score in zip(names, scores):
    print(name, score)



#Type checking and conversions
value = "123"
# type checking
print(type(value))
# conversion
num = int(value)
print(num, type(num))
# float conversion
f = float(value)
print(f, type(f))
