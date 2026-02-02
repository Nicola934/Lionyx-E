fruits = ["apple", "banana", "organge"]

print("Add items:")

fruits.append("mango")
fruits.insert(1, "grape")

print("Remove items:")

fruits.remove("banana")

print("Check")

"apple" in fruits

print("Looping")

for f in fruits:
    print(f)