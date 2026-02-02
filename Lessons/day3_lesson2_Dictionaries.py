print("Lesson 3: Dictionaries")


student = {"name": "Nicola", "age": 19, "course": "GPython"}

print("Access:")

print("Access name:")
name = student["name"]
print(name)

print("Access age: ")
age = student.get("age")
print(age)

print("Add email")

email = student["email"] = "nicolamaluleke12@gmail.com"
print(email)

print("Update age")
student["age"] = 21
age = student["age"]
print(age)

print("Remove course")

student.pop("course")
print("course removed successfully")


print("\n--- STUDENT DETAILS ---")

for key, value in student.items():
    print(f"{key}", value)