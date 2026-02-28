import math
#1
degree = float(input("Input degree: "))
radian = degree * (math.pi / 180)
print(f"Output radian: {radian:.6f}")

#2
height = float(input("Height: "))
base_1 = float(input("Base, first value: "))
base_2 = float(input("Base, second value: "))
area = ((base_1 + base_2) / 2) * height
print(f"Expected Output: {area}")

#3
n_sides = int(input("Input number of sides: "))
side_length = float(input("Input the length of a side: "))
area = (n_sides * side_length**2) / (4 * math.tan(math.pi / n_sides))
print(f"The area of the polygon is: {area:.0f}")

#4
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))
area = base * height
print(f"Expected Output: {area}")