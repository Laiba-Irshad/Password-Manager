import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

def connect_db():
    conn=psycopg2.connect(
        host="localhost",
        database="Password-Generator",
        user="postgres",
        password="libs_3007",
        port = "5432"
    )
    return conn

def create_users_table():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
            );

            """
        )
        conn.commit()
        print("Table created Successfully!")
    except Exception as e:
        print(f"An error occured: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def create_passwords_table():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
               CREATE TABLE IF NOT EXISTS passwords(
               id SERIAL PRIMARY KEY,
               user_id INT REFERENCES users(id) ON DELETE CASCADE,
               services VARCHAR(255) UNIQUE NOT NULL,
               password TEXT NOT NULL,
               created_at TIMESTAMP DEFAULT NOW()
               );
            """
        )
        conn.commit()
        print("Passwords Table created Successfully!")
    except Exception as e:
        print(f"An error occured: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()