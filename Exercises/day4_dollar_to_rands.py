print("Exercise 3: Function that returns a value")

def convert_to_rands(dollars):
    ratio = 18
    dollars_in_rands = dollars * ratio

    return dollars_in_rands

dollars = int(input("Enter amount in dollars: "))
rands = convert_to_rands(dollars)

print(f"\n${dollars:,.2f} = R{rands:,.2f}")
input()