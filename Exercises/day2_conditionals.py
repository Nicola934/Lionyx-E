print("== Lionyx-E Access Control System ===")

username = input("Enter your username: ")
password = input("Enter your password: ")

# Simple authentication logic

if username == "admin" and password == "lionyx123":
    print("Login successful!")

    role = input("Enter you role (owner/admin/staff/guest): ")

    if role == "owner":
        print("Full system access granted.")
    elif role == "admin":
        print("Admin-level access granted.")
    elif role == "staff":
        print("Limited tools access granted.")
    else:
        print("Guest access only")

else:
    print("Incorrect login. Access denied.")