# src/db_manager.py
import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",      # Sesuaikan dengan user MySQL Anda
            password="Iqra26022005",      # Sesuaikan dengan password MySQL Anda
            database="db_arsip"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error saat menghubungkan ke database: {e}")
        return None