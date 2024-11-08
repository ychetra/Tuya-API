from dotenv import load_dotenv
import os
import pyodbc

load_dotenv()

def get_db_connection():
    """Create and return a database connection using environment variables"""
    try:
        connection_string = (
            f'DRIVER={os.getenv("DB_DRIVER")};'
            f'SERVER={os.getenv("DB_SERVER")};'
            f'DATABASE={os.getenv("DB_NAME")};'
            f'Trusted_Connection={os.getenv("DB_TRUSTED_CONNECTION")};'
        )
        print(f"Attempting to connect with: {connection_string}")  # Debug connection string
        
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        # List available drivers
        print("\nAvailable ODBC drivers:")
        for driver in pyodbc.drivers():
            print(f"  - {driver}")
        raise

if __name__ == "__main__":
    # Test the connection
    try:
        conn = get_db_connection()
        print("Successfully connected to database!")
        conn.close()
    except Exception as e:
        print(f"Connection test failed: {e}")