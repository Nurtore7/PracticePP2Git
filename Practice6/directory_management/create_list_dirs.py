import os

print("Current directory:")
print(os.getcwd())

os.mkdir("test_folder")
os.makedirs("parent_folder/child_folder", exist_ok=True)

print("\nContents of current directory:")
print(os.listdir())

os.chdir("test_folder")
print("\nChanged directory:")
print(os.getcwd())

os.chdir("..")
os.rmdir("test_folder")

print("\nFolder test_folder removed.")