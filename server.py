import socket	# Provides network socket interface
import ssl		# Enables encrypted socket communication
import sqlite3	# Interfaces with SQLite database
import os		# File and system-level operations
from datetime import datetime  # Used to generate timestamp for logs
import threading	# Handles multiple client connections
import random	# Used to assign a random port for ssl connection


#Handles client requests (inputs)
def handle_client(conn, addr):
    print(f"Connection from {addr}")
    try:
        while True:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                break

            parts = data.strip().split(',')
            command = parts[0]

			#Ticket purchase input handle
            if command == "purchase_ticket":
                genre, artist, quantity, first, last, email, payment_info = parts[1:]
                quantity = int(quantity)

                conn_db = sqlite3.connect("Concert_data.db")
                cursor = conn_db.cursor()
				
				#Find TicketID with it's attributes
                cursor.execute("""
                    SELECT TICKET.TicketID, TICKET.AvailableTickets, TICKET.Price
                    FROM TICKET
                    JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID
                    WHERE ARTIST.Genre = ? AND ARTIST.Name = ?
                """, (genre, artist))
                ticket = cursor.fetchone()

                if ticket:
                    ticket_id, available, price = ticket
                    if available >= quantity:
                        # Update availability in the database
                        cursor.execute("UPDATE TICKET SET AvailableTickets = AvailableTickets - ? WHERE TicketID = ?", (quantity, ticket_id))

                        # Insert customer purchase with quantity and payment details
                        cursor.execute("""
                            INSERT INTO CUSTOMER (FirstName, LastName, Email, PaymentInfo, PurchasedTicketID, Quantity)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (first, last, email, payment_info, ticket_id, quantity))

                        conn_db.commit()
                        
                        # Generate timestamped log entry
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_line = f"{timestamp} | PURCHASE | {first} {last} bought {quantity} ticket(s) for {artist} in {genre} at ${price} each | Payment Info: {payment_info} | Email: {email}\n"

                       # Write the same entry to both logs
                       # Logging behavior: purchase/cancel actions are tracked here
                        with open("transactions.log", "a") as log, open("leaked_logs.txt", "a") as leak:
                            log.write(log_line)
                            leak.write(log_line)
                            
						# Inform client of successful purchase
                        conn.send(f"Successfully purchased {quantity} ticket(s) for {artist}.".encode('utf-8'))
                    
                    # Inform client if not enough tickets are available
                    else:
                        conn.send(f"Only {available} ticket(s) available for {artist}.".encode('utf-8'))
               
               # Inform client if no ticket record was found
                else:
                    conn.send(f"No ticket info found for {artist} in {genre}.".encode('utf-8'))

                conn_db.close()
	
			#List tickets by genre
            elif command == "list_tickets_by_genre":
                if len(parts) >= 2:
                    genre = parts[1]
                    try:
                        conn_db = sqlite3.connect("Concert_data.db")
                        cursor = conn_db.cursor()
                        cursor.execute('''
                            SELECT ARTIST.Name, MIN(TICKET.Price)
                            FROM TICKET
                            JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID
                            WHERE LOWER(ARTIST.Genre) = LOWER(?)
                            GROUP BY ARTIST.Name
                        ''', (genre,))
                        results = cursor.fetchall()
                        conn_db.close()

                        if not results:
                            conn.send(f"No artists available under genre {genre}.".encode('utf-8'))
                        else:
                            artist_lines = [f"{name} (${price})" for name, price in results]
                            response = "\n".join(artist_lines)
                            conn.send(response.encode('utf-8'))
                    except Exception as e:
                        print("[SERVER ERROR - GENRE]", e)
                        conn.send("Error fetching artists from database.".encode('utf-8'))
                else:
                    conn.send("Genre parameter missing.".encode('utf-8'))
			
			#List customer's ourchased tickets by email
            elif command == "list_user_tickets":
                email = parts[1]
                try:
                    conn_db = sqlite3.connect("Concert_data.db")
                    cursor = conn_db.cursor()
                    cursor.execute("""
                        SELECT ARTIST.Name, SUM(CUSTOMER.Quantity)
                        FROM CUSTOMER
                        JOIN TICKET ON CUSTOMER.PurchasedTicketID = TICKET.TicketID
                        JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID
                        WHERE LOWER(CUSTOMER.Email) = LOWER(?)
                        GROUP BY ARTIST.Name
                    """, (email,))
                    rows = cursor.fetchall()
                    conn_db.close()

                    if not rows:
                        conn.send("No tickets found under your email.".encode('utf-8'))
                    else:
                        ticket_summary = "\n".join([f"{artist}: {qty} ticket(s)" for artist, qty in rows])
                        conn.send(ticket_summary.encode('utf-8'))
                except Exception as e:
                    print("[SERVER ERROR - TICKET LIST]", e)
                    conn.send("Failed to fetch ticket info.".encode('utf-8'))

            elif command == "cancel_purchase":
                email, artist = parts[1], parts[2]
                try:
                    conn_db = sqlite3.connect("Concert_data.db")
                    cursor = conn_db.cursor()
                    
                    # Find the matching ticket by email and artist
                    cursor.execute("""
                        SELECT CustomerID, Quantity
                        FROM CUSTOMER
                        JOIN TICKET ON CUSTOMER.PurchasedTicketID = TICKET.TicketID
                        JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID
                        WHERE LOWER(CUSTOMER.Email) = LOWER(?) AND LOWER(ARTIST.Name) = LOWER(?)
                        ORDER BY CustomerID DESC
                        LIMIT 1
                    """, (email, artist))
                    result = cursor.fetchone()

					# If multiple tickets exist, decrement. Otherwise, delete the record.
                    if result:
                        customer_id, qty = result
                        if qty > 1:
                            cursor.execute("UPDATE CUSTOMER SET Quantity = Quantity - 1 WHERE CustomerID = ?", (customer_id,))
                        else:
                            cursor.execute("DELETE FROM CUSTOMER WHERE CustomerID = ?", (customer_id,))
                        conn_db.commit()

						# Log cancellation with timestamp
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_line = f"{timestamp} | CANCEL | {email} canceled a ticket for {artist}\n"
                        
                        # Write to both primary and leaked log files
        			    # Logging behavior: purchase/cancel actions are tracked here
                        with open("transactions.log", "a") as log, open("leaked_logs.txt", "a") as leak:
                            log.write(log_line)
                            leak.write(log_line)

                        conn.send(f"Cancelled your most recent ticket for {artist}.".encode('utf-8'))
                    
                    #No record matching user's cancellation request
                    else:
                        conn.send("No matching ticket found to cancel.".encode('utf-8'))
                    conn_db.close()
                except Exception as e:
                    print("[SERVER ERROR - CANCEL]", e)
                    conn.send("Error processing cancellation.".encode('utf-8'))

            elif command == "verify_ticket":
                last_name = parts[1]
                try:
                    conn_db = sqlite3.connect("Concert_data.db")
                    cursor = conn_db.cursor()
                    
                    # Retrieve all ticket purchases where the last name matches 
                    cursor.execute("""
                        SELECT FirstName, LastName, Email, ARTIST.Name, ARTIST.Genre, ARTIST.ConcertDate, ARTIST.Venue, TICKET.Price
                        FROM CUSTOMER
                        JOIN TICKET ON CUSTOMER.PurchasedTicketID = TICKET.TicketID
                        JOIN ARTIST ON TICKET.ArtistID = ARTIST.ArtistID
                        WHERE LOWER(CUSTOMER.LastName) = LOWER(?)
                    """, (last_name,))
                    results = cursor.fetchall()
                    conn_db.close()

					#Informs user of ticket not found
                    if not results:
                        conn.send("No ticket found for that last name.".encode('utf-8'))
                        
                    #Used to return verified ticket information to user
                    else:
                        response = ""
                        for row in results:
                            response += (
                                f"Customer Name: {row[0]} {row[1]}\n"
                                f"Email: {row[2]}\n"
                                f"Artist: {row[3]}\n"
                                f"Genre: {row[4]}\n"
                                f"Concert Date: {row[5]}\n"
                                f"Venue: {row[6]}\n"
                                f"Price: ${row[7]}\n\n"
                            )
                            
                        # Send all matching ticket info to the client
                        conn.send(response.encode('utf-8'))
                        
                # Handle server-side error during verification
                except Exception as e:
                    print("[SERVER ERROR - VERIFY]", e)
                    conn.send("Error verifying ticket.".encode('utf-8'))
			
            else:
                conn.send("Invalid command.".encode('utf-8'))

#Catches any Python error in the handle_client execution and prints the error message in the server terminal
    except Exception as e:
        print("[SERVER ERROR - CLIENT HANDLING]", e)
    finally:
        conn.close()

# Initializes and starts the secure server, binding to a random port and allows multiple secessions of the program to be ran simultaneously
def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    secure_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), certfile='cert.pem', keyfile='key.pem', server_side=True)

    port = random.randint(45000, 55000)
    secure_socket.bind(('127.0.0.1', port))
    secure_socket.listen(5)

    with open("server_port.txt", "w") as f:
        f.write(str(port))

    print(f"Secure server started on 127.0.0.1:{port}")

    while True:
        client_conn, addr = secure_socket.accept()
        threading.Thread(target=handle_client, args=(client_conn, addr)).start()

if __name__ == "__main__":
    main()

