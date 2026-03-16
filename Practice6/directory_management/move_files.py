import os
import shutil

os.makedirs("backup_folder", exist_ok=True)

print("Text files in current directory:")
for file in os.listdir():
    if file.endswith(".txt"):
        print(file)

shutil.copy("sample.txt", "backup_folder/sample.txt")
print("File copied to backup_folder.")

shutil.move("backup_folder/sample.txt", "backup_folder/moved_sample.txt")
print("File renamed/moved inside backup_folder.")