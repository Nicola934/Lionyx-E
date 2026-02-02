

print("Exercise 3 - Data Entry Rule Logic")

hours = 6
speed_fast = True

if hours >= 4 and speed_fast:
    print("Full-day rate applied")
elif hours >= 4 and not speed_fast:
    print("Reduced rate.")
else:
    print("Half-day rate.")
    