import re
txt = "The rain in Spain"
x = re.search("ai", txt)
print(x) #this will print an object


#.span()-returns a tuple containing the start-, and end positions of the match.
import re
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.span())


#.string-returns the string passed into the function
import re
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.string)


#.group()-returns the part of the string where there was a match
import re
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.group())