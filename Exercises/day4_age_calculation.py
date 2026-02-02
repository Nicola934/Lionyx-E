print("Exercise 2: Function with parameters\n")

def calculate_age(current_year, birth_year):
    age = current_year - birth_year
    return age

birth_year = 2006
current_year = 2025

age = calculate_age(current_year, birth_year)

print(f"I was born in {birth_year} and I turned {age} in {current_year}")

input()