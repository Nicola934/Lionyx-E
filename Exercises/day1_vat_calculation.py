print("Exercise 3: Vat Calculation")

vat = 0.15
print("Enter the product's price: ")
price = float(input())

vat_amount = price*vat

print(f"The vat amount is R{vat_amount:,.2f}")

print("------------------------")