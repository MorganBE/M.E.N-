import socket
import sqlite3

""" 
Name: Morgan E. Brown, Niy'Asia Williams, Erin C. Vickers
Instructor: Peker, Yesem K
Description: Server program that'll allow communication to commit concert tickets purchases,
and verifications
Date: 26 March 2025
Version: 1.0
"""


# Database creation with 3 Tables ARTIST, TICKET, CUSTOMER
def create_table():
    """Create the users table if it doesn't exist."""
    conn = sqlite3.connect('Concert_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ARTIST (
            ArtistID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Genre TEXT NOT NULL,
            ConcertDate TEXT NOT NULL,
            Venue TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        Create TABLE IF NOT EXISTS TICKET(
        TicketID INTEGER PRIMARY KEY AUTOINCREMENT,
        ArtistID INTEGER NOT NULL,
        Price REAL,
        AvailableTickets INTEGER NOT NULL
        FOREIGN KEY (ArtistID) REFERENCES ARTIST (ArtistID)
        )
    ''')
    cursor.exectue('''
    Create TABLE IF NOT EXISTS CUSTOMER(
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT NOT NULL,
    PaymentInfo, TEXT NOT NULL,
    PurchasedTicketID INTEGER NOT NULL,
    FOREIGN KEY (PurchasedTicketID) REFERENCES TICKET (TicketID)
    )
    
    ''')
    conn.commit()
    conn.close()
    #Handling Request
