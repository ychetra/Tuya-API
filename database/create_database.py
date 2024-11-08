from dotenv import load_dotenv
import os
import pyodbc

load_dotenv()

def create_database():
    try:
        conn = pyodbc.connect(
            f'DRIVER={os.getenv("DB_DRIVER")};'
            f'SERVER={os.getenv("DB_SERVER")};'
            'DATABASE=master;'
            f'Trusted_Connection={os.getenv("DB_TRUSTED_CONNECTION")};'
        )
        
        cursor = conn.cursor()
        
        cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{os.getenv("DB_NAME")}')
        BEGIN
            CREATE DATABASE {os.getenv("DB_NAME")};
        END
        """)
        
        print("Database created successfully!")
        
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_database() 