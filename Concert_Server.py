import socket
import ssl
import sqlite3
import threading

def create_table():
    conn = sqlite3.connect('Concert_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ARTIST (
            ArtistID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL UNIQUE,
            Genre TEXT NOT NULL,
            ConcertDate TEXT NOT NULL,
            Venue TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TICKET (
            TicketID INTEGER PRIMARY KEY AUTOINCREMENT,
            ArtistID INTEGER NOT NULL,
            AvailableTickets INTEGER NOT NULL,
            Price REAL NOT NULL,
            FOREIGN KEY (ArtistID) REFERENCES ARTIST(ArtistID)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CUSTOMER (
            CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Email TEXT NOT NULL,
            PaymentInfo TEXT NOT NULL,
            PurchasedTicketID INTEGER NOT NULL,
            FOREIGN KEY (PurchasedTicketID) REFERENCES TICKET(TicketID)
        )
    ''')

    artists = [
        ('Future', 'Hip Hop', '15 July 2025', 'Atlanta'),
        ('Drake', 'Hip Hop', '12 May 2025', 'New York'),
        ('Usher', 'R&B', '16 June 2025', 'Los Angeles'),
        ('SZA', 'R&B', '19 August 2025', 'Houston'),
        ('Lady Gaga', 'Pop', '20 September 2025', 'Dallas'),
        ('Ariana Grande', 'Pop', '29 October 2025', 'Atlanta'),
        ('Eagles', 'Rock', '5 December 2025', 'Columbus'),
        ('AC/DC', 'Rock', '2 November 2025', 'Detroit'),
        ('Flipturn', 'Indie', '30 April 2025', 'Los Angeles'),
        ('MGMT', 'Indie', '30 June 2025', 'Houston')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO ARTIST (Name, Genre, ConcertDate, Venue)
        VALUES (?, ?, ?, ?)
    ''', artists)

    tickets = [
        (1, 100, 300.0), (2, 150, 500.0), (3, 120, 275.0), (4, 140, 280.0),
        (5, 200, 350.0), (6, 180, 325.0), (7, 160, 300.0), (8, 100, 310.0),
        (9, 90, 250.0), (10, 110, 270.0)
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO TICKET (ArtistID, AvailableTickets, Price)
        VALUES (?, ?, ?)
    ''', tickets)

    conn.commit()
    conn.close()

def handle_list_tickets_by_genre(genre):
    conn = sqlite3.connect('Concert_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT ARTIST.Name
        FROM TICKET
        JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID
        WHERE LOWER(ARTIST.Genre) = LOWER(?)
    ''', (genre,))
    artists = cursor.fetchall()
    conn.close()

    if not artists:
        return f"No artists available under genre {genre}."

    response = ""
    for artist in artists:
        response += f"{artist[0]}\n"
    return response

def handle_list_tickets():
    conn = sqlite3.connect('Concert_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT TICKET.TicketID, ARTIST.Name, TICKET.Price, TICKET.AvailableTickets
        FROM TICKET JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID
    ''')
    tickets = cursor.fetchall()
    conn.close()

    if not tickets:
        return "No tickets available."

    response = ""
    for ticket_id, artist, price, available in tickets:
        response += f"ID: {ticket_id} | Artist: {artist} | Price: ${price} | Available: {available}\n"
    return response

def handle_client(conn, addr):
    print(f"Connection from {addr}")
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"[Client]: {data}")

            parts = data.strip().split(',')
            command = parts[0]

            if command == "list_tickets":
                response = handle_list_tickets()

            elif command == "list_tickets_by_genre":
                genre = parts[1]
                response = handle_list_tickets_by_genre(genre)

            elif command == "purchase_ticket":
                genre, artist, qty = parts[1], parts[2], int(parts[3])
                first, last, email, payment = parts[4:8]

                conn_db = sqlite3.connect('Concert_data.db')
                cursor = conn_db.cursor()
                cursor.execute("SELECT TICKET.TicketID, AvailableTickets FROM TICKET JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID WHERE ARTIST.Name = ?", (artist,))
                row = cursor.fetchone()

                if not row:
                    response = "Artist not found."
                else:
                    ticket_id, available = row
                    if available < qty:
                        response = "Not enough tickets available."
                    else:
                        cursor.execute("UPDATE TICKET SET AvailableTickets = AvailableTickets - ? WHERE TicketID = ?", (qty, ticket_id))
                        cursor.execute("INSERT INTO CUSTOMER (FirstName, LastName, Email, PaymentInfo, PurchasedTicketID) VALUES (?, ?, ?, ?, ?)", (first, last, email, payment, ticket_id))
                        conn_db.commit()
                        response = f"Successfully purchased {qty} ticket(s) for {artist}."
                conn_db.close()

            elif command == "add_ticket":
                artist_name, price, quantity = parts[1], float(parts[2]), int(parts[3])
                conn_db = sqlite3.connect('Concert_data.db')
                cursor = conn_db.cursor()
                cursor.execute("SELECT ArtistID FROM ARTIST WHERE Name = ?", (artist_name,))
                result = cursor.fetchone()

                if not result:
                    response = f"Artist '{artist_name}' not found."
                else:
                    artist_id = result[0]
                    cursor.execute("INSERT INTO TICKET (ArtistID, AvailableTickets, Price) VALUES (?, ?, ?)", (artist_id, quantity, price))
                    conn_db.commit()
                    response = f"Ticket for {artist_name} added successfully."
                conn_db.close()

            elif command == "delete_ticket":
                ticket_id = int(parts[1])
                conn_db = sqlite3.connect('Concert_data.db')
                cursor = conn_db.cursor()
                cursor.execute("DELETE FROM TICKET WHERE TicketID = ?", (ticket_id,))
                conn_db.commit()
                conn_db.close()
                response = f"Ticket ID {ticket_id} deleted successfully."

            else:
                response = "Invalid command."

            conn.send(response.encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        print(f"Disconnected from {addr}")

def run_server():
    create_table()
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_socket = ssl.wrap_socket(
        server_socket,
        server_side=True,
        certfile="server_cert.pem",
        keyfile="server_key.pem",
        ssl_version=ssl.PROTOCOL_TLS
    )

    try:
        secure_socket.bind((host, port))
    except OSError as e:
        print(f"Port {port} is already in use. Please free it before running again.")
        return

    secure_socket.listen(5)
    print(f"Secure server started on {host}:{port}")

    while True:
        conn, addr = secure_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    run_server()