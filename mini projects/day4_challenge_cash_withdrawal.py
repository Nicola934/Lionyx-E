print("Challenge: Bank Withdrawal\n")

def bank_withdraw(balance, amount):
    if amount > balance:
        print("Insufficient funds!")
        return -1
    else:
     print("Withdrawal successful!")
     new_balance = balance - amount
    return new_balance

def display(amount, balance):
   if balance != -1:
      print(f"Cash withdrawal: R{amount:,.2f} Avail: R{balance:,.2f}")

amount = float(input("Enter withdrawal amount: "))
bank_balance = float(input("Enter bank balance: "))

balance = bank_withdraw(bank_balance, amount)

display(amount, balance)
input()
