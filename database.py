import sqlite3

def create_connection(database):
    conn = sqlite3.connect(database)
    return conn

def add_subscriber(conn, phone_number):
    query = "INSERT INTO subscribers (phone_number, opted_in, opted_in_at) VALUES (?, 1, datetime('now'))"
    cur = conn.cursor()
    cur.execute(query, (phone_number,))
    conn.commit()

def remove_subscriber(conn, phone_number):
    query = "UPDATE subscribers SET opted_in = 0 WHERE phone_number = ?"
    cur = conn.cursor()
    cur.execute(query, (phone_number,))
    conn.commit()

def is_subscriber_opted_in(conn, phone_number):
    query = "SELECT opted_in FROM subscribers WHERE phone_number = ?"
    cur = conn.cursor()
    cur.execute(query, (phone_number,))
    result = cur.fetchone()
    return result and result[0] == 1

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL UNIQUE,
            opted_in BOOLEAN DEFAULT 1
        )
    """)
    conn.commit()
