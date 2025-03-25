import sqlite3
""" 
Name: Morgan E. Brown
Instructor: Peker, Yesem K
Description: Modification of the SQLite program we went over in class to include the new field (column) "last_name" in the database while also altering
             the "name" column to "first_name".
Date: 10 February, 2025
Version: 1.2
"""
def create_table():
    """Create the users table if it doesn't exist."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            address TEXT NOT NULL,
            balance REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(input_firstname, input_lastname, input_address,  input_balance,):
    """Add a new user with their address to the database."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (first_name, last_name, address, balance) VALUES (?, ?, ?, ?)', (input_firstname,input_lastname, input_address, input_balance))
        conn.commit()
        print(f"User '{input_firstname} {input_lastname}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"User '{input_firstname} {input_lastname}' already exists.")
    conn.close()

def get_all_users():
    """Retrieve all users and their addresses from the database."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT first_name, last_name, address, balance FROM users')
    users = cursor.fetchall()
    conn.close()
    return users
    
def get_user(input_firstname):
    """Retrieve user with first name."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE first_name = ?', (input_firstname,))
    #cursor.execute('SELECT * FROM users WHERE name = ?', (input_firstname,))
    user = cursor.fetchall()
    conn.close()
    return user

def get_users_by_last_name(input_lastname):
   """Retrieve user with last name.
   I decided to include a last name search query option"""
   conn = sqlite3.connect('user_data.db')
   cursor = conn.cursor()
   cursor.execute('SELECT * FROM users WHERE last_name = ?', (input_lastname,))
   users = cursor.fetchall()
   conn.close()
   return users

# Main Program
if __name__ == "__main__":
    create_table()
    add_user('Morgan', 'Brown', '123 sesame st', 500.0)
    add_user('Anothny', 'Davis', '2500 Victory Ave', 200.0)
    add_user('Abraham', 'Lincoln', '2 lincoln memorial cir', 0.0)
    add_user('Trae', 'Young', '1 Philips Drive', 50.0)

    while True:
        print("\nMenu:")
        print("1. Add a user")
        print("2. View all users and their info")
        print("3. Find user by first name")
        print("4. Find user with last name")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            customer_firstname = input("Enter the first name: ")
            customer_lastname = input("Enter the last name: ")
            customer_address = input("Enter the address: ")
            customer_balance=input("Enter the balance: ")
            add_user(customer_firstname, customer_lastname, customer_address, customer_balance)
        elif choice == '2':
            users = get_all_users()
            if users:
                print("\nUser Information:")
                for first_name, last_name, address, balance in users: #can use any variable instead of user, address, balance
                    print(first_name, last_name, address, balance) #us eteh same variable set you used in previous line
            else:
                print("\nNo users found.")
        elif choice == '3':
            customer_name = input("Enter first name: ")
            user = get_user(customer_firstname)
            if user:
                print(user)
            else:
                print("\nNo users found.")
        elif choice == '4':
           customer_lastname = input("Enter last name: ")
           users = get_users_by_last_name(customer_lastname)
           if users:
               print(users)
           else:
               print("\nNo users found.")
        elif choice =='5':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

