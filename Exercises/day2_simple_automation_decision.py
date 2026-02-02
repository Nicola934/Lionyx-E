print ("Day 2 Exercises: Basic Data Validationg")

print("Exercise 1")

username = input("Enter username: ")

if len(username) == 0:
    print("Error: Username required.")
else:
    print("Username accepted")

print("---------------------------")

print("Exercise 2: Simple Automation Decision")

file_name = "data.csv"

if file_name.endswith(".csv"):
    print("Processing CSV...")
else:
    print("Unsupported file type.")

print("-----------------------------")