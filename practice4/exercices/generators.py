# 1. Generator that generates squares of numbers up to N
def squares_up_to(n):
    for i in range(n + 1):
        yield i ** 2

n = int(input("Enter N: "))
print("Squares up to N:")
for value in squares_up_to(n):
    print(value, end=" ")
print("\n")


# 2. Even numbers between 0 and n in comma-separated form
def even_numbers(n):
    for i in range(0, n + 1, 2):
        yield i

n = int(input("Enter n for even numbers: "))
print("Even numbers:")
print(",".join(str(num) for num in even_numbers(n)))
print()


# 3. Numbers divisible by 3 and 4 between 0 and n
def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input("Enter n for divisible numbers: "))
print("Numbers divisible by 3 and 4:")
for num in divisible_by_3_and_4(n):
    print(num, end=" ")
print("\n")


# 4. Generator squares(a, b)
def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

a = int(input("Enter a: "))
b = int(input("Enter b: "))
print("Squares from a to b:")
for val in squares(a, b):
    print(val, end=" ")
print("\n")


# 5. Generator that returns numbers from n down to 0
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

n = int(input("Enter n for countdown: "))
print("Countdown:")
for num in countdown(n):
    print(num, end=" ")
print()