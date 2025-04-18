#Ticket Purchasing System - Final Project
#Morgan Brown, Erin Vickers, Niy'Asia Williams
#Yesem Peker
#April 21, 2025


import socket	# Used to establish the network connection to the server
import ssl	# Secures the client-server communication using SSL/TLS
import re 	# Used for input validation with special characters (e.g., email format)


#Displays main menu options to the user
def genre_menu():
    print("\nWelcome to M.E.N concert ticketing purchasing menu!")
    print("1. Purchase a ticket")
    print("2. Add to my ticket purchase")
    print("3. Cancel my ticket purchase")
    print("4. Verify ticket information")
    print("5. Exit")
    return input("Enter your choice: ")
    
#Displays genre options for the user to choose from
def select_genre():
    print("\nPlease choose a Genre: ")
    print("1. Hip Hop")
    print("2. R&B")
    print("3. Pop")
    print("4. Rock")
    print("5. Indie")
    return input("Enter the number matching your choice: ")
    

def display_artists_by_genre(genre, wrapped_socket):
	#Sends a request to the server for artist in the selected genre
    wrapped_socket.send(f"list_tickets_by_genre,{genre}".encode('utf-8'))
    artist_data = wrapped_socket.recv(4096).decode('utf-8')
    
    #Parses & displays the artist list returned by the user
    artists = [line.strip() for line in artist_data.strip().splitlines() if line.strip()]
    if not artists:
        print("No artists found.")
        return []
    print(f"\nArtists in {genre} with Ticket Prices:")
    for i, artist in enumerate(artists):
        print(f"{i+1}. {artist}")
    return artists

#Collects/Validates first name, last name, email 
def get_valid_user_info():
    while True:
        first = input("First name: ").strip()
        if not first.isalpha():
            print("First name must contain only letters.")
            continue

        last = input("Last name: ").strip()
        if not last.isalpha():
            print("Last name must contain only letters.")
            continue

        email = input("Email: ").strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Invalid email format.")
            continue

        return first, last, email

#Collects/Validates card #, expriation date, cvv
def get_valid_card_info():
    while True:
        print("\nPlease enter your payment information:")
        card_number = input("Card Number (16 digits): ").strip()
        exp_date = input("Expiration Date (MM/YY): ").strip()
        cvv = input("CVV (3 digits): ").strip()

        if not card_number.isdigit() or len(card_number) != 16: #caud # must be 16 numeric digits
            print("Invalid card number. Please enter exactly 16 digits.")
            continue
        if not exp_date or len(exp_date) != 5 or exp_date[2] != '/' or not (exp_date[:2].isdigit() and exp_date[3:].isdigit()):
            print("Expiration date must be in MM/YY format.") #Expiration must be in MM/YY format numerically
            continue
        if not cvv.isdigit() or len(cvv) != 3:
            print("CVV (must be exactly 3 digits).") #CVV must be a 3-digit numeric value
            continue

        return f"{card_number} | {exp_date} | {cvv}"

#Process of purchasing a ticket from genre to confirmation
def purchase_ticket_flow(wrapped_socket):
    genre_map = {"1": "Hip Hop", "2": "R&B", "3": "Pop", "4": "Rock", "5": "Indie"}

    while True:
        genre_choice = select_genre() #User selects a genre
        if genre_choice not in genre_map:
            print("Invalid genre selection.")
            continue

        genre = genre_map[genre_choice] #connects the user's choice to the list of artists
        
        artist_list = display_artists_by_genre(genre, wrapped_socket) #request & display lists of artists from selected genre
        if not artist_list:
            return

		#User confirms or changes genre selection
        proceed = input("Would you like to purchase from this genre? (yes to continue / no to pick another genre): ").strip().lower()
        if proceed == "yes":
            break

	#Prompt for ticket purchase
    artist_index = input("Enter the number matching the artist: ") 
    try:
        artist_index = int(artist_index) - 1
        if 0 <= artist_index < len(artist_list):
            full_line = artist_list[artist_index]
            artist = full_line.split(" ($")[0]
            price_str = full_line.split(" ($")[1].replace(")", "")
            ticket_price = float(price_str)
			
            quantity = int(input(f"Enter the number of tickets for {artist}: "))

            total_price = ticket_price * quantity
            print(f"Total price: ${total_price:.2f}")
			
            print("\nPlease enter your customer info:")
            first, last, email = get_valid_user_info()
            payment = get_valid_card_info()

            request = f"purchase_ticket,{genre},{artist},{quantity},{first},{last},{email},{payment}"
            wrapped_socket.send(request.encode('utf-8'))
            response = wrapped_socket.recv(4096).decode('utf-8')
            print(response)
        else:
            print("Invalid artist selection.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

#Allows user to add more tickets to the existing purchase
def addTicket(wrapped_socket):
    print("\nAdd to Your Ticket Purchase")
    genre_map = {"1": "Hip Hop", "2": "R&B", "3": "Pop", "4": "Rock", "5": "Indie"}

    while True:
        genre_choice = select_genre()
        if genre_choice not in genre_map:
            print("Invalid genre selection.")
            continue

        genre = genre_map[genre_choice]
        artist_list = display_artists_by_genre(genre, wrapped_socket)
        if not artist_list:
            return

        proceed = input("Would you like to add a ticket from this genre? (yes/no): ").strip().lower()
        if proceed == "yes":
            break

    artist_index = input("Enter the number matching the artist: ")
    try:
        artist_index = int(artist_index) - 1
        if 0 <= artist_index < len(artist_list):
            full_line = artist_list[artist_index]
            artist = full_line.split(" ($")[0]

            quantity = int(input(f"How many additional tickets for {artist} would you like to purchase?: "))
            print(f"This will add {quantity} more ticket(s) for {artist}.")

            confirm = input("Confirm? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Add cancelled.")
                return

            print("\nPlease re-enter your name and email to match your previous ticket:")
            first, last, email = get_valid_user_info()
            payment = get_valid_card_info()

            request = f"purchase_ticket,{genre},{artist},{quantity},{first},{last},{email},{payment}"
            wrapped_socket.send(request.encode('utf-8'))
            response = wrapped_socket.recv(4096).decode('utf-8')
            print(response)
        else:
            print("Invalid artist selection.")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")

#Cancels a single ticket by email & artist 
def cancelMyPurchase(wrapped_socket):
    print("\nCancel My Ticket Purchase")
    email = input("Enter your email to view your ticket summary: ").strip()
    wrapped_socket.send(f"list_user_tickets,{email}".encode('utf-8'))
    response = wrapped_socket.recv(4096).decode('utf-8')

    if response.startswith("No tickets"):
        print(response)
        return

    print("\nYour Ticket Purchases:")
    print(response)

    artist = input("\nEnter the artist you want to cancel a ticket for: ").strip()
    request = f"cancel_purchase,{email},{artist}"
    wrapped_socket.send(request.encode('utf-8'))
    result = wrapped_socket.recv(4096).decode('utf-8')
    print(result)

#Sends last name to server to look up ticket details
def verify_ticket(wrapped_socket):
    last_name = input("What is your last name: ").strip()
    wrapped_socket.send(f"verify_ticket,{last_name}".encode('utf-8'))
    response = wrapped_socket.recv(4096).decode('utf-8')
    if not response.startswith("No ticket"):
        print("\nYour Ticket Information:\n" + response)
    else:
        print(response)
    input("\nPress Enter to return to the main menu...")

#Reads server port, establishes SSL connection, & handles menu loop
def main():
    host = 'localhost'
    try:
        with open("server_port.txt", "r") as f:
            port = int(f.read().strip())
    except Exception:
        print("Failed to read server_port.txt. Make sure the server is running.")
        return

    print("Welcome to the M.E.N Ticketing System!")

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    wrapped_socket = context.wrap_socket(client_socket)
    wrapped_socket.connect((host, port))

    while True:
        choice = genre_menu()
        if choice == '1':
            purchase_ticket_flow(wrapped_socket)
        elif choice == '2':
            addTicket(wrapped_socket)
        elif choice == '3':
            cancelMyPurchase(wrapped_socket)
        elif choice == '4':
            verify_ticket(wrapped_socket)
        elif choice == '5':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    wrapped_socket.close()

if __name__ == "__main__":
    main()

