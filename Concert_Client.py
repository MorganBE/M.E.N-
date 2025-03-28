import socket
import sqlite3
""" 
Name: Morgan E. Brown, Niy'Asia Williams, Erin C. Vickers
Instructor: Peker, Yesem K
Description: 
Date: 26 March 2025
Version: 1.0
"""

#def add_user(input_firstname, input_lastname, input_address,  input_balance,):
#"""Add a new user with their address to the database."""
#conn = sqlite3.connect('user_data.db')
#cursor = conn.cursor()
#try:
#cursor.execute('INSERT INTO users (first_name, last_name, address, balance) VALUES (?, ?, ?, ?)', (input_firstname,input_lastname, input_address, input_balance))
#conn.commit()
#print(f"User '{input_firstname} {input_lastname}' added successfully.")
#except sqlite3.IntegrityError:
#print(f"User '{input_firstname} {input_lastname}' already exists.")
#conn.close()

#def get_all_users():
#"""Retrieve all users and their addresses from the database."""
#conn = sqlite3.connect('user_data.db')
#cursor = conn.cursor()
#cursor.execute('SELECT first_name, last_name, address, balance FROM users')
#users = cursor.fetchall()
#conn.close()
#return users

#def get_user(input_firstname):
#"""Retrieve user with first name."""
#conn = sqlite3.connect('user_data.db')
#cursor = conn.cursor()
#cursor.execute('SELECT * FROM users WHERE first_name = ?', (input_firstname,))
##cursor.execute('SELECT * FROM users WHERE name = ?', (input_firstname,))
#user = cursor.fetchall()
#conn.close()
#return user

#def get_users_by_last_name(input_lastname):
#"""Retrieve user with last name.
#I decided to include a last name search query option"""
#conn = sqlite3.connect('user_data.db')
#cursor = conn.cursor()
#cursor.execute('SELECT * FROM users WHERE last_name = ?', (input_lastname,))
#users = cursor.fetchall()
#conn.close()
#return users
# ^^ Above are functions we can use to create our own ^^
# Main Program
if __name__ == "__main__":
    create_table()

    while True:
        print("\nWelcome to M.E.N concert ticketing purchasing menu!")
        print("Through our private chat channel you will be able to choose your favorite artist through their "
              "infamous genre's.")
        print("1. Genre")
        print("2. Add or Delete Ticket")
        print("3. Lookup Concert Info")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            customer_firstname = input("Enter the first name: ")
            customer_lastname = input("Enter the last name: ")
            customer_address = input("Enter the address: ")
            customer_balance=input("Enter the balance: ")
            #add_user(customer_firstname, customer_lastname, customer_address, customer_balance)
        elif choice == '2':
            #users = get_all_users()
            if users:
               # print("\nUser Information:")
               # for first_name, last_name, address, balance in users: #can use any variable instead of user, address, balance
                   # print(first_name, last_name, address, balance) #us eteh same variable set you used in previous line
            else:
                #print("\nNo users found.")
        elif choice == '3':
            #customer_name = input("Enter first name: ")
            #user = get_user(customer_firstname)
            if user:
               # print(user)
            else:
                print("\nNo users found.")
        elif choice == '4':
            #customer_lastname = input("Enter last name: ")
            #users = get_users_by_last_name(customer_lastname)
            if users:
               # print(users)
            else:
               # print("\nNo users found.")
        elif choice =='5':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


