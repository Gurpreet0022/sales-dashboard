# File 2: init_db.py
# This script initializes the SQLite database with schema and data

import sqlite3

def init_db():
    connection = sqlite3.connect("ecommerce.db")
    cursor = connection.cursor()

    with open("database_setup.sql", "r") as f:
        sql_script = f.read()
        cursor.executescript(sql_script)

    connection.commit()
    connection.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
