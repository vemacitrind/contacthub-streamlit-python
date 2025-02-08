import mysql.connector , mysql.connector.errors

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="contacthub"
    )
