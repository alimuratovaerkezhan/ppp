#File_handling
#Create a text file and write sample data
with open("sample.txt", "w") as f:
    f.write("Hello, world!\n")
    f.write("This is a sample file.\n")


#Read and print file contents
with open("sample.txt", "r") as f:
    content = f.read()
    print(content)


#Append new lines and verify content
with open("sample.txt", "a") as f:
    f.write("This line is appended.\n")

with open("sample.txt", "r") as f:
    print(f.read())


#Copy and back up files using shutil
import shutil

shutil.copy("sample.txt", "backup_sample.txt")


#Delete files safely
import os

file_path = "backup_sample.txt"

if os.path.exists(file_path):
    os.remove(file_path)
    print("File deleted")
else:
    print("File not found")