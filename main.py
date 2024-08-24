import re
import hashlib
import getpass
from cryptography.fernet import Fernet
import base64

user_accounts={}
password_manager={}

def generate_key(master_password):
    key = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(key[:32])

def encrypt_password(plain_text, key):
    fernet = Fernet(key)
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_password(encrypted_text , key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text.encode()).decode()

def is_strong_password(password):
    if (len(password) >= 8 and re.search(r"\d",password) and re.search(r"[A-z]",password) and re.search(r"[a-z]",password) and re.search(r"[@#$%&*^-_!><?/|]",password)):
        return True
    return False

def create_account(): 
    username = input("Enter your desired username:\t")
    while True:
        password = getpass.getpass("Enter your desired password:\t")
        if is_strong_password(password):
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_accounts[username] = hashed_password
            print("Account created Succesfully!")
            break
        else:
            print("Password must be 8 characters long, an uppercase letter, a lower case letter , and a special character1")

def login():
    username = input("Enter your desired username:\t")
    password = getpass.getpass("Enter your desired password:\t")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if username in user_accounts and user_accounts[username] == hashed_password:
        print("login succesfull!")
        return username
    else:
        print("Invalid username or password.")
        return None

def reset_password():
    username=input("Enter your desired username:\t")
    if username in password_manager:
        old_password = getpass.getpass("Enter your current password:\t")
        hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
        if password_manager[username] == hashed_old_password:
            while True:
                new_password = getpass.getpass("Enter your nre password;\t")
                if is_strong_password(new_password):
                    hashed_new_password = hashlib.sha256(password.encode()).hexdigest()
                    user_accounts[username] = hashed_new_password
                    print("Password reset successfully!")
                    break
                else:
                    print("Password must be strong.")
        else:
            print("Incorrect Current Password")
    else:
        print("Username not found")

def delete_account():
    username = input("Enter your desired username:\t")
    if username in password_manager:
        password = getpass.getpass("Enter your desired password:\t")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user_accounts[username] == hashed_password:
            del user_accounts[username]
            if username in password_manager:
                del password_manager[username]
            print("Account deleted Successfully!")
        else:
            print("Password is incorrect")
    else:
        print("Username not found")

# def view_username():
#     if password_manager:
#         print("Registered Usernames:\n")
#         for username in password_manager.keys():
#             print(username)
#     else:
#         print("No account found")

def add_password(username):
    service = input("Enter the service name:\t")
    service_password = getpass.getpass("Enter Password for this service.\n")
    key = generate_key(user_accounts[username])
    encrypted_password = encrypt_password(service_password,key)
    if username not in password_manager:
        password_manager[username] = {}
    password_manager[username][service] = encrypted_password
    print(f"Password for Service '{service}' added Successfully!")

def retrieve_password(username):
    service = input("Enter the service name:\t")
    if username in password_manager and service in password_manager[username]:
        key = generate_key(user_accounts[username])
        encrypted_password = password_manager[username][service]
        decrypted_password = decrypt_password(encrypted_password,key)
        print(f"Password for '{service}':'{decrypted_password}'")
    else:
        print(f"No passwpord found for '{service}'")

def update_password(username):
    service = input("Enter the service name:\t")
    if username in password_manager and service in password_manager[username]:
        service_password = getpass.getpass("Enter the new password for this service")
        key = generate_key(user_accounts[username])
        encrypted_password = password_manager[username][service]
        password_manager[username][service] = encrypted_password
        print(f"Password for '{service}' updated Successfully!")
    else:
        print(f"No password found for '{service}'")

def delete_password(username):
    service = input("Enter the service name:\t")
    if username in password_manager and service in password_manager[username]:
        del password_manager[username][service]
        print(f"Password for '{service}' deleted Successfully!")
    else:
        print(f"No password found for '{service}'")

def view_all_services(username):
    if username in password_manager and password_manager[username]:
        print("Your saved Services:\n")
        for service in password_manager[username]:
            print(service)
    else:
        print("No service found.")
       
def main():
    while True:
        print("\nMENU")
        print("1: Create an account")
        print("2: Login")
        print("3: Reset password")
        print("4: Delete account")
        print("0: Exit")
        choice = input("Enter your choice:\t")

        if choice == '1':
            create_account()
        elif choice == '2':
            username = login()
            if username:
                while True:
                    print("\nPassword Manager Menu:\n")
                    print("a: Add a Password")
                    print("b: Retrieve a Password")
                    print("c: Update a Password")
                    print("d: Delete a Password")
                    print("e: View all saved Services")
                    print("f: Log out")
                    pm_choice = input("Enter your Choice:\t")
                    if pm_choice == "a":
                        add_password(username)
                    elif pm_choice == "b":
                        retrieve_password(username)
                    elif pm_choice == "c":
                        update_password(username)
                    elif pm_choice == "d":
                        delete_password(username)
                    elif pm_choice == "e":
                        view_all_services(username)
                    elif pm_choice == "f":
                        print("Logging out...")
                        break
                    else:
                        print("Invalid Choice, Please try again.")
        
        elif choice == 3:
            reset_password()
        elif choice == 4:
            delete_account()
        elif choice == 0:
            print("Exiting the Program... Goodbye!")
            break
        else:
            print("Invalid Choice, Please try again.")

if __name__ == "__main__":
    main()



