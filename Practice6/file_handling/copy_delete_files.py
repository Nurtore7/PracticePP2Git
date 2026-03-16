import shutil
import os

shutil.copy("sample.txt", "backup.txt")
print("File copied successfully.")

if os.path.exists("backup.txt"):
    os.remove("backup.txt")
    print("Backup file deleted successfully.")
else:
    print("File does not exist.")