from database.db_utils import get_db_connection

def drop_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Drop device_status first due to foreign key constraint
        cursor.execute('''
        IF OBJECT_ID('device_status', 'U') IS NOT NULL
            DROP TABLE device_status;
        ''')

        # Then drop devices table
        cursor.execute('''
        IF OBJECT_ID('devices', 'U') IS NOT NULL
            DROP TABLE devices;
        ''')

        conn.commit()
        print("Tables dropped successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    drop_tables() 