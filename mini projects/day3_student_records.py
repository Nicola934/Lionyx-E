print("--- Student Records ---")

students = []

while True:
    print("\n-- Add a Student Record ---")
    name = input("Enter studet name: ")
    course = input("Enter course: ")
    score = float(input("Enter score(0-100): "))

    student = {"name": name, "course": course, "score": score}
    students.append(student)
    
    more = input("Add another? (y/n): ").lower()
    if more != "y":
        break;

print("\n === STUDENT REPORT ===")

for s in students:
    print(f"{s['name']} | {s['course']} | Score: {s['score']}")
input()