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
