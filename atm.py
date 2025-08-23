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
            print(f"Database connection failed.: {err}")
            return False

    def close_db(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            
    def login(self):
        print("\n--- Login ---")
        username = input("Enter the username: ")
        password = input("Enter the password: ")

        self.cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = self.cursor.fetchone()

        if user_data:
            self.logged_in_user = user_data
            print(f"\n✅ Login successful! Welcome, {self.logged_in_user['username']}!")
            return True
        else:
            print("❌ Incorrect username or password.")
            return False

    def check_balance(self):
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        self.cursor.execute("SELECT balance FROM users WHERE user_id = %s", (self.logged_in_user['user_id'],))
        current_balance = self.cursor.fetchone()['balance']
        print(f"\nCurrent balance in the account: ₹{current_balance:.2f}")

    def deposit(self):
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        try:
            amount = float(input("Enter the amount you wish to deposit: "))
            if amount <= 0:
                print("❌ The amount must be greater than zero.")
                return

            self.cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, self.logged_in_user['user_id']))
            self.connection.commit()
            print(f"✅ ₹{amount:.2f} Deposited into your account.")
            self.check_balance()

        except ValueError:
            print("❌ Invalid amount. Please enter a number.")
            
    def withdraw(self):
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        try:
            amount = float(input("Enter the amount you wish to withdraw:"))
            if amount <= 0:
                print("❌  The amount must be greater than zero. ")
                return

            self.cursor.execute("SELECT balance FROM users WHERE user_id = %s", (self.logged_in_user['user_id'],))
            current_balance = self.cursor.fetchone()['balance']

            if amount > current_balance:
                print("❌ There is not enough money in the account.")
            else:
                self.cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, self.logged_in_user['user_id']))
                self.connection.commit()
                print(f"✅ ₹{amount:.2f} Withdrawn.")
                self.check_balance()
        except ValueError:
            print("❌ Invalid amount. Please enter a number.")

    def change_password(self):
        if not self.logged_in_user:
            print("❌ Please log in first.")
            return

        current_password = input("Enter current password.: ")
        if current_password != self.logged_in_user['password']:
            print("❌ The current password is incorrect.")
            return

        new_password = input("Enter new password: ")
        confirm_password = input("Confirm new password: ")
        
        if new_password != confirm_password:
            print("❌ The new passwords do not match.")
            return

        self.cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, self.logged_in_user['user_id']))
        self.connection.commit()
        self.logged_in_user['password'] = new_password
        print("✅ Password changed successfully.")

    def logout(self):
        print(f"\nGoodbye, {self.logged_in_user['username']}! 👋")
        self.logged_in_user = None

    def display_menu(self):
        print("\n--- ATM Menu ---")
        print("1. Check balance")
        print("2. Deposit money")
        print("3. Withdraw money")
        print("4. Change password")
        print("0. Logout")

    def run(self):
        if not self.connect_db():
            return

        while True:
            if not self.logged_in_user:
                if self.login():
                    self.main_loop()
            else:
                # Should not reach here if main_loop handles it correctly.
                pass
            
            choice = input("\nPress '1' to log in again, or '0' to exit: ")
            if choice == '0':
                break
        
        self.close_db()
        print("Bye See You Again")

    def main_loop(self):
        while self.logged_in_user:
            self.display_menu()
            choice = input("Enter your choice.: ")

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
                    print("❌ Invalid selection. Please select the numbers in the menu.")
            except Exception as e:
                print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    # Database connection parameters
    atm = ATM("localhost", "root", "", "atm_db")
    atm.run()