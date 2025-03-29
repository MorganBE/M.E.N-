import socket
import ssl

def genre_menu():
    print("\nWelcome to M.E.N concert ticketing purchasing menu!")
    print("1. What genre ticket would you like to purchase?")
    print("2. Would you like to modify a purchase?")
    print("3. Exit")
    return input("Enter your choice: ")

def select_genre():
    print("\nPlease choose a Genre: ")
    print("1. Hip Hop")
    print("2. R&B")
    print("3. Pop")
    print("4. Rock")
    print("5. Indie")
    return input("Enter the number matching your choice: ")

def display_artists_by_genre(genre, wrapped_socket):
    wrapped_socket.send(f"list_tickets_by_genre,{genre}".encode('utf-8'))
    artist_data = wrapped_socket.recv(4096).decode('utf-8')
    artists = artist_data.strip().split('\n')
    if artists[0].startswith("No artists"):
        print(artist_data)
        return []
    print(f"\nArtists in {genre}:")
    for i, artist in enumerate(artists):
        print(f"{i+1}. {artist}")
    return artists

def purchase_ticket_flow(wrapped_socket):
    genre_choice = select_genre()
    genre_map = {"1": "Hip Hop", "2": "R&B", "3": "Pop", "4": "Rock", "5": "Indie"}

    if genre_choice in genre_map:
        genre = genre_map[genre_choice]
        artist_list = display_artists_by_genre(genre, wrapped_socket)
        if not artist_list:
            return

        artist_index = input("Enter the number matching the artist: ")
        try:
            artist_index = int(artist_index) - 1
            if 0 <= artist_index < len(artist_list):
                artist = artist_list[artist_index]
                quantity = input(f"Enter the number of tickets for {artist}: ")

                print("\nPlease enter your customer info:")
                first = input("First name: ")
                last = input("Last name: ")
                email = input("Email: ")
                payment = input("Payment Info: ")

                request = f"purchase_ticket,{genre},{artist},{quantity},{first},{last},{email},{payment}"
                wrapped_socket.send(request.encode('utf-8'))
                response = wrapped_socket.recv(4096).decode('utf-8')
                print(response)
            else:
                print("Invalid artist selection.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    else:
        print("Invalid genre selection.")

def add_or_delete_ticket_flow(wrapped_socket):
    action = input("\nPress (a) to add a ticket ").lower()

    if action == 'a':
        print("\n--- Add Ticket ---")
        artist = input("Enter artist name: ")
        price = input("Enter ticket price: ")
        quantity = input("Enter ticket quantity: ")
        request = f"add_ticket,{artist},{price},{quantity}"
        wrapped_socket.send(request.encode('utf-8'))
        response = wrapped_socket.recv(4096).decode('utf-8')
        print(response)

    elif action == 'd':
        print("\n--- Delete Ticket ---")
        wrapped_socket.send("list_tickets".encode('utf-8'))
        ticket_data = wrapped_socket.recv(4096).decode('utf-8')
        print("\nAvailable Tickets:")
        print(ticket_data)
        ticket_id = input("Enter the Ticket ID to delete: ")
        request = f"delete_ticket,{ticket_id}"
        wrapped_socket.send(request.encode('utf-8'))
        response = wrapped_socket.recv(4096).decode('utf-8')
        print(response)
    else:
        print("Invalid option.")

def main():
    host = 'localhost'
    port = 12345

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
            add_or_delete_ticket_flow(wrapped_socket)
        elif choice == '3':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    wrapped_socket.close()

if __name__ == "__main__":
    main()

