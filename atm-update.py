# ATM System with MySQL Database Integration
# Features: User Authentication, Balance Inquiry, Deposit, Withdrawal, Password Change, Transaction Logging
# MySQL ലെ രണ്ട് ടേബിളുകളും ഇതിൽ ഉപയോഗിക്കുന്നുണ്ട്. ഓരോ ട്രാൻസാക്ഷൻസും കൃത്യമായി ട്രാൻസാക്ഷൻ എന്ന 
# ടേബിളിൽ രേഖപ്പെടുത്തി വെയ്ക്കുന്നുണ്ട്.
import mysql.connector

class ATM:
    def __init__(self, host, user, password, database):
        self.db_host = host
        self.db_user = user
        self.db_password = password
        self.db_database = database
        self.connection = None
        self.cursor = None
        self.logged_in_user = None

    def connect_db(self):
        """Establishes a connection to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            return False

    def close_db(self):
        """Closes the database connection."""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            
    def _log_transaction(self, transaction_type, amount=None):
        """Logs a transaction into the transactions table."""
        if not self.logged_in_user:
            return
        
        sql = "INSERT INTO transactions (user_id, transaction_type, amount) VALUES (%s, %s, %s)"
        values = (self.logged_in_user['user_id'], transaction_type, amount)
        
        try:
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error logging transaction: {err}")

    def login(self):
        """Handles user login."""
        print("\n--- Login ---")
        username = input("Enter username: ")
        password = input("Enter password: ")

        self.cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = self.cursor.fetchone()

        if user_data:
            self.logged_in_user = user_data
            print(f"\n✅ Login successful! Welcome, {self.logged_in_user['username']}!")
            return True
        else:
            print("❌ Invalid username or password.")
            return False

    def check_balance(self):
        """Displays the current account balance."""
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        self.cursor.execute("SELECT balance FROM users WHERE user_id = %s", (self.logged_in_user['user_id'],))
        current_balance = self.cursor.fetchone()['balance']
        print(f"\nYour current balance is: ₹{current_balance:.2f}")

    def deposit(self):
        """Handles depositing money into the account."""
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        try:
            amount = float(input("Enter amount to deposit: "))
            if amount <= 0:
                print("❌ The amount must be greater than zero.")
                return

            self.cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, self.logged_in_user['user_id']))
            self.connection.commit()
            print(f"✅ ₹{amount:.2f} has been deposited to your account.")
            self._log_transaction('deposit', amount)
            self.check_balance()

        except ValueError:
            print("❌ Invalid amount. Please enter a number.")
            
    def withdraw(self):
        """Handles withdrawing money from the account."""
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        try:
            amount = float(input("Enter amount to withdraw: "))
            if amount <= 0:
                print("❌ The amount must be greater than zero.")
                return

            self.cursor.execute("SELECT balance FROM users WHERE user_id = %s", (self.logged_in_user['user_id'],))
            current_balance = self.cursor.fetchone()['balance']

            if amount > current_balance:
                print("❌ Insufficient balance.")
            else:
                self.cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, self.logged_in_user['user_id']))
                self.connection.commit()
                print(f"✅ ₹{amount:.2f} has been withdrawn.")
                self._log_transaction('withdraw', amount)
                self.check_balance()
        except ValueError:
            print("❌ Invalid amount. Please enter a number.")

    def change_password(self):
        """Allows the user to change their password."""
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        current_password = input("Enter your current password: ")
        if current_password != self.logged_in_user['password']:
            print("❌ Incorrect current password.")
            return

        new_password = input("Enter a new password: ")
        confirm_password = input("Confirm the new password: ")
        
        if new_password != confirm_password:
            print("❌ New passwords do not match.")
            return

        self.cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, self.logged_in_user['user_id']))
        self.connection.commit()
        self.logged_in_user['password'] = new_password
        print("✅ Password changed successfully.")
        self._log_transaction('password_change')

    def logout(self):
        """Logs the user out."""
        print(f"\nGoodbye, {self.logged_in_user['username']}! 👋")
        self.logged_in_user = None

    def display_menu(self):
        """Displays the main ATM menu."""
        print("\n--- ATM Menu ---")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Change Password")
        print("0. Logout")

    def run(self):
        """Main program loop to handle user interaction."""
        if not self.connect_db():
            return

        while True:
            if not self.logged_in_user:
                if self.login():
                    self.main_loop()
            else:
                # This part is unreachable as main_loop() handles the logic.
                pass
            
            choice = input("\nPress '1' to log in again, or '0' to exit: ")
            if choice == '0':
                break
        
        self.close_db()
        print("Program terminated.")

    def main_loop(self):
        """The main loop after a successful login."""
        while self.logged_in_user:
            self.display_menu()
            choice = input("Enter your choice: ")

            try:
                if choice == '1':
                    self.check_balance()
                elif choice == '2':
                    self.deposit()
                elif choice == '3':
                    self.withdraw()
                elif choice == '4':
                    self.change_password()
                elif choice == '0':
                    self.logout()
                    break
                else:
                    print("❌ Invalid choice. Please select a number from the menu.")
            except Exception as e:
                print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    # Update these with your MySQL database credentials
    atm = ATM("localhost", "root", "", "atm_db")
    atm.run()
    
    # What it if __name__ == "__main__":? does?
    # This line checks if the script is being run directly (not imported as a module).
    # If it is run directly, it creates an instance of the ATM class and calls the run() method to start the program.
    # __name__ == "__main__":  എന്നത് പൈത്തൺ സ്ക്രിപ്റ്റ് നേരിട്ട് റൺ ചെയ്യപ്പെടുമ്പോൾ മാത്രമേ ആ ഭാഗം എക്സിക്യൂട്ട് ചെയ്യപ്പെടൂ.
    # ഇത് സ്ക്രിപ്റ്റ് മറ്റൊരു മോഡ്യൂളിൽ നിന്ന് ഇംപോർട്ട് ചെയ്യപ്പെടുമ്പോൾ ആ ഭാഗം എക്സിക്യൂട്ട് ചെയ്യപ്പെടാതിരിക്കാൻ സഹായിക്കുന്നു.
# What is the use of if __name__ == "__main__": in Python?
# In Python, if __name__ == "__main__": is used to check whether a script is being run directly or being imported as a module in another script.
# When a Python script is run directly, the special variable __name__ is set to "__main__".
# If the script is imported as a module, __name__ is set to the module's name.
# By using if __name__ == "__main__":, you can ensure that certain code
# only runs when the script is executed directly, and not when it is imported.
# This is useful for testing or running code that should not execute when the module is imported elsewhere.
# Example:
# def main():
#     print("This script is being run directly.")   
# if __name__ == "__main__":
#     main()
# In this example, the main() function will only be called if the script is run directly.

    
    # What is the use of self in Python?
    # In Python, self is a reference to the current instance of the class.  It is used to access variables and methods associated with the instance.
    # It must be the first parameter of any function in the class.
    # It allows you to differentiate between instance variables and local variables within methods.
    # It is a convention to name it self, but you can use any name you like.
    
    # What is the use of __init__ method in Python?
    # The __init__ method in Python is a special method that is called when an instance of a class is created.
    # It is used to initialize the attributes of the class. 
    
    # How many methods are there in the ATM class?
    # There are 16 methods in the ATM class: 
    # __init__, connect_db, close_db, _log_transaction, login, check_balance, 
    # deposit, withdraw, change_password, logout, display_menu, run, main_loop
    # The __init__ method is the constructor that initializes the ATM object with database connection parameters.
    # The connect_db method establishes a connection to the MySQL database.
    # The close_db method closes the database connection.
    # The _log_transaction method logs each transaction into the transactions table.
    # The login method handles user authentication.
    # The check_balance method displays the current account balance.
    # The deposit method allows users to deposit money into their account.
    # The withdraw method allows users to withdraw money from their account.
    # The change_password method allows users to change their account password.
    # The logout method logs the user out of the system.
    # The display_menu method shows the main ATM menu options.
    # The run method is the main program loop that handles user interaction.
    # The main_loop method handles the logic after a successful login.
    # Each method has a specific purpose and contributes to the overall functionality of the ATM system.
    # The __init__ method initializes the ATM object with database connection parameters.
    # The connect_db method establishes a connection to the MySQL database.
    # The close_db method closes the database connection.
    # The _log_transaction method logs each transaction into the transactions table.
    # The login method handles user authentication.
    # The check_balance method displays the current account balance.
    # The deposit method allows users to deposit money into their account.
    # The withdraw method allows users to withdraw money from their account.
    # The change_password method allows users to change their account password.
    # The logout method logs the user out of the system.
    # The display_menu method shows the main ATM menu options.
    # The run method is the main program loop that handles user interaction.
    # The main_loop method handles the logic after a successful login.
    # Each method has a specific purpose and contributes to the overall functionality of the ATM system.

# .cursor(dictionary=True) എന്ന് എന്തിനാണ് ഉപയോഗിക്കുന്നത്?
# .cursor(dictionary=True) എന്നത് MySQL Connector/Python ൽ ഉപയോഗിക്കുന്ന ഒരു ഓപ്ഷനാണ്.
# ഇത് ക്വറി ഫലങ്ങൾ ഡിക്ഷണറി രൂപത്തിൽ ലഭ്യമാക്കാൻ സഹായിക്കുന്നു.
# സാധാരണയായി, ക്വറി ഫലങ്ങൾ ട്യൂപ്പിളുകളായി ലഭ്യമിക്കും,
# എന്നാൽ dictionary=True ഉപയോഗിച്ചാൽ, ഫലങ്ങൾ കാളം പേരുകൾ കീ ആയി ഉപയോഗിച്ച് ഡിക്ഷണറിയായി ലഭിക്കും.
# ഉദാഹരണത്തിന്, ഒരു ക്വറി ഫലം (1, 'rajesh', 1000) എന്ന ട്യൂപ്പിള്‍ ആയി ലഭിക്കുമ്പോള്‍,
# dictionary=True ഉപയോഗിച്ചാല്‍ {'user_id': 1, 'username': 'rajesh', 'balance': 1000} എന്ന ഡിക്ഷണറിയായി ലഭിക്കും.
# ഇത് കോഡ് വായിക്കാൻ എളുപ്പമാക്കുന്നു, കാരണം നിങ്ങൾക്ക് കാളം പേരുകൾ ഉപയോഗിച്ച് മൂല്യങ്ങൾ ആക്‌സസ് ചെയ്യാം.
# ഉദാഹരണത്തിന്, user_data['username'] എന്നത് user_data[1] എന്നതിനെക്കാൾ കൂടുതൽ വായിക്കാൻ എളുപ്പമാണ്.

# What is the use of commit() in Python MySQL?
# In Python MySQL, the commit() method is used to save the changes made to the database.
# When you execute an INSERT, UPDATE, or DELETE statement, the changes are not immediately saved to the database.
# Instead, they are held in a transaction until you call commit().
# Calling commit() makes all changes made in the current transaction permanent.
# If you do not call commit(), the changes will be lost when the connection is closed or if a rollback is performed.
# It is important to call commit() after making changes to ensure that your data is saved correctly.

# cursor എന്ന മെത്തേഡ് ഉപയോഗിക്കുന്നത് എന്തിനാണ്? ഡാറ്റാബേസുമായി എങ്ങനെ കമ്യൂണിക്കേറ്റ് ചെയ്യാൻ സഹായിക്കുന്നു?
# cursor എന്ന മെത്തേഡ് ഡാറ്റാബേസുമായി കമ്യൂണിക്കേറ്റ് ചെയ്യാൻ സഹായിക്കുന്നു.
# ഇത് ഡാറ്റാബേസിൽ ക്വറികൾ എക്സിക്യൂട്ട് ചെയ്യാനും ഫലങ്ങൾ റിട്ടേൺ ചെയ്യാനും ഉപയോഗിക്കുന്നു.
# cursor മെത്തേഡ് ഉപയോഗിച്ച്, നിങ്ങൾക്ക് SQL ക്വറികൾ തയ്യാറാക്കാനും എക്സിക്യൂട്ട് ചെയ്യാനും കഴിയും.
# ഉദാഹരണത്തിന്, SELECT, INSERT, UPDATE, DELETE തുടങ്ങിയ ക്വറികൾ cursor ഉപയോഗിച്ച് എക്സിക്യൂട്ട് ചെയ്യാം.
# cursor.execute() മെത്തേഡ് ഉപയോഗിച്ച് ക്വറി എക്സിക്യൂട്ട് ചെയ്യാം.
# cursor.fetchone() മെത്തേഡ് ഉപയോഗിച്ച് ഒരു റെക്കോർഡ് റിട്ടേൺ ചെയ്യാം.
# cursor.fetchall() മെത്തേഡ് ഉപയോഗിച്ച് എല്ലാ റെക്കോർഡുകളും റിട്ടേൺ ചെയ്യാം.
# cursor.close() മെത്തേഡ് ഉപയോഗിച്ച് കർസർ ക്ലോസ് ചെയ്യാം.
# cursor എന്നത് ഒരു ഡാറ്റാബേസ് കണക്ഷനിൽ നിന്ന് ഒരു കർസർ ഒബ്ജക്റ്റ് സൃഷ്ടിക്കുന്നതിന് ഉപയോഗിക്കുന്ന മെത്തേഡ് ആണ്.

# ക്ലാസ് എന്നത് എന്താണ്? Python ൽ ക്ലാസ് എങ്ങനെ നിർവചിക്കാം?
# ക്ലാസ് എന്നത് ഒരു ടെംപ്ലേറ്റ് അല്ലെങ്കിൽ ബ്ലൂപ്രിന്റ് ആണ്,
# ഇത് ഒബ്ജക്റ്റുകൾ സൃഷ്ടിക്കാൻ ഉപയോഗിക്കുന്നു.
# Python ൽ ക്ലാസ് നിർവചിക്കാൻ, class കീവേഡ് ഉപയോഗിച്ച് ഒരു ക്ലാസ് ഡിഫൈൻ ചെയ്യാം.
# ഉദാഹരണത്തിന്: 
# class MyClass:
#     def __init__(self, attribute1, attribute2):   
#         self.attribute1 = attribute1
#         self.attribute2 = attribute2
#     def my_method(self):
#         return self.attribute1 + self.attribute2
# ഈ ഉദാഹരണത്തിൽ, MyClass എന്ന ക്ലാസ് രണ്ട് ആട്രിബ്യൂട്ടുകളും ഒരു മെത്തേഡും ഉൾക്കൊള്ളുന്നു.
# __init__ മെത്തേഡ് ക്ലാസ് ഇൻസ്റ്റൻസ് സൃഷ്ടിക്കുമ്പോൾ ഓട്ടോമാറ്റിക്കായി വിളിക്കപ്പെടുന്നു.
# self എന്നത് ക്ലാസ് ഇൻസ്റ്റൻസിനെ സൂചിപ്പിക്കുന്നു.
# ക്ലാസ് ഇൻസ്റ്റൻസ് സൃഷ്ടിക്കാൻ, ക്ലാസ് നാമം ഉപയോഗിച്ച് ഒരു വേരിയബിൾ നിർവചിക്കാം.
# ഉദാഹരണത്തിന്:
# my_object = MyClass(10, 20)
# ഇതു my_object എന്ന ക്ലാസ് ഇൻസ്റ്റൻസ് സൃഷ്ടിക്കും, attribute1 10 ആയും attribute2 20 ആയും സജ്ജമാക്കും.
# ക്ലാസ് ഇൻസ്റ്റൻസ് മെത്തേഡുകൾ ആക്‌സസ് ചെയ്യാൻ, ഡോട്ട് നോട്ടേഷൻ ഉപയോഗിക്കാം.
# ഉദാഹരണത്തിന്:
# result = my_object.my_method()
# ഇത് my_method() മെത്തേഡ് വിളിച്ച് attribute1, attribute2 യുടെ കൂട്ടം റിട്ടേൺ ചെയ്യും.
# ക്ലാസ് ഒരു ഒബ്ജക്റ്റ്-ഓറിയന്റഡ് പ്രോഗ്രാമിംഗ് (OOP) കോൺസെപ്റ്റാണ്,
# ഇത് കോഡ് റിയൂസബിലിറ്റി, മെയിന്റനബിലിറ്റി, എക്സ്റ്റൻസിബിലിറ്റി എന്നിവ മെച്ചപ്പെടുത്താൻ സഹായിക്കുന്നു.

# What is the use of try and except in Python?
# In Python, try and except are used for exception handling.
# The try block contains code that may potentially raise an exception.
# If an exception occurs, the code in the except block is executed.
# This allows you to handle errors gracefully without crashing the program.
# Example:
# try:
#     result = 10 / 0
# except ZeroDivisionError:
#     print("Cannot divide by zero.")
# In this example, the code inside the try block raises a ZeroDivisionError.
# The except block catches the exception and prints an error message instead of crashing the program.
# Using try and except helps in managing errors and exceptions effectively,
# ensuring that the program can continue running or fail gracefully.

