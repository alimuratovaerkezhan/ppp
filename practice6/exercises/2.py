#Directory
#Create nested directories
import os
os.makedirs("folder/subfolder", exist_ok=True)

#List files and folders
files = os.listdir(".")
for file in files:
    print(file)


#Find files by extension
for file in os.listdir("."):
    if file.endswith(".txt"):
        print(file)


#Move/copy files between directories
import shutil

shutil.copy("sample.txt", "folder/sample.txt")  # copy
shutil.move("sample.txt", "folder/sample_moved.txt")  # move
