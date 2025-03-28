import socket
import sqlite3

""" 
Name: Morgan E. Brown, Niy'Asia Williams, Erin C. Vickers
Instructor: Peker, Yesem K
Description: 
Date: 26 March 2025
Version: 1.0
"""


def genre_menu():
    print("\n Please choose a Genre: ")
    print("1. Hip Hop")
    print("2. R&B")
    print("3. Pop")
    print("4. Rock")
    print("5. Indie")
    choice = input("Enter the number matching your choice: ")
    return choice


def artist_menu(genre):
    print(f"\n Artist available in {genre}")
    print("Option 1")
    print("Option 2")
    choice = input("Enter the number associated with your option: ")
    return choice


if __name__ == "__main__":

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    while True:
        print("\nWelcome to M.E.N concert ticketing purchasing menu!")
        print("Through our private chat channel you will be able to choose your favorite artist through their "
              "infamous genre's.")
        print("1. What genre ticket would you like to purchase?")
        print("2. Would you like to add or delete Ticket?")
        print("3. Would you like to lookup or update concert information?")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            genre_menu_choice = genre_menu()
            genres = {"1": "Hip Hop", "2": "R&B", "3": "Pop", "4": "Rock", "5": "Indie"}
            if genre_menu_choice in genres:
                genre = genres[genre_menu_choice]
                artist_menu_choice = artist_menu(genre)
                artist = {"1 ": "Artist A", "2 ": "Artist B"}
                if artist_menu_choice in artist:
                    artist = artist[artist_menu_choice]
                    num_tickets = input(f"Enter the number of tickets for {artist}: ")
                    request = f"purchase_ticket,{genre},{artist},{num_tickets}"
                    client_socket.send(request.encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    print(response)
                else:
                    print("Invalid artist selection.")
            else:
                print("Invalid genre selection.")


        # elif choice == '2':

        # if :

        # else:
        # print("")
        # elif choice == '3':

        # if user:
        ## print()
        # else:
        # print("\nNo users found.")
        elif choice == '4':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
