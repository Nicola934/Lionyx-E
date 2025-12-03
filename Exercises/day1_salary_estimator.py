









print("Exercise 5: Salary Estimator")

tax_rate = 0.18

print("Enter hourly rate: ")
hourly_rate = float(input())
print("Enter hours per day")
daily_hours = float(input())
print("Enter days per month")
month_days = int(input())

monthly_income = (hourly_rate*daily_hours) * month_days
yearly_income = monthly_income * 12
tax = yearly_income * tax_rate

print (f"Your monthly income is R{monthly_income:,.2f}, yearly income is R{yearly_income:,.2f} and your estimated tax payment is R{tax:,.2f}")