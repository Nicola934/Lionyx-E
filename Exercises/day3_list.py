print("Exercise 1:")

daily_tasks = [ "Bath", "Clean up", "Eat", "Recieve Money", "Write Code", "Make more money" ]

daily_tasks.append("Enjoy money")
daily_tasks.append("Drive")

daily_tasks.remove("Bath")
daily_tasks.remove("Drive")

no_of_tasks = len(daily_tasks)

print(f"Total number of tasks: {no_of_tasks}")

print("All Tasks:")

for f in daily_tasks:
    print(f)