import sqlite3

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
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
