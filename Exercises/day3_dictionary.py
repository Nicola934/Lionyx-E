print("Exercise 3: Product Dictionary")

Laptop = {"name": "Laptop", "price": 30000, "stock": 20}

print("\nAdding stock:")

current_stock = Laptop["stock"]
print(f"\nCurrent stock number: {current_stock}")

print("Adding 20+ stock...")

Laptop["stock"] += 20
updated_stock = Laptop["stock"]
print(f"\nUpdated stock number: {updated_stock}")

print("\nApplying 10% discount:")
discount = 0.1
original_price = Laptop["price"]
print(f"Price before discount: R{Laptop["price"]:,.2f} ")

discounted_price = Laptop["price"] - (Laptop["price"] * discount)
Laptop["price"] = discounted_price
print(f"Discounted price: R{discounted_price:,.2f}")

print("\n --- Product details ---")
for key, value in Laptop.items():
    print(f"{key}", value)


input()

