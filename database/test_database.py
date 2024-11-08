from database.db_utils import get_db_connection
import pyodbc

def test_database_setup():
    try:
        # Test connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        
        tables = cursor.fetchall()
        print("\nExisting tables:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Show table structure
            cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table[0]}'")
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"  - {col[3]}: {col[7]}")
        
        # Check if any data exists
        if 'devices' in [t[0] for t in tables]:
            cursor.execute("SELECT COUNT(*) FROM devices")
            device_count = cursor.fetchone()[0]
            print(f"\nNumber of devices: {device_count}")
            
            if device_count > 0:
                cursor.execute("SELECT * FROM devices")
                print("\nDevices data:")
                for row in cursor.fetchall():
                    print(row)
        
        if 'device_status' in [t[0] for t in tables]:
            cursor.execute("SELECT COUNT(*) FROM device_status")
            status_count = cursor.fetchone()[0]
            print(f"\nNumber of status records: {status_count}")
            
            if status_count > 0:
                cursor.execute("""
                    SELECT TOP 5 
                        device_id, 
                        timestamp, 
                        switch_1
                    FROM device_status 
                    ORDER BY timestamp DESC
                """)
                print("\nLatest status records:")
                for row in cursor.fetchall():
                    print(row)
                    
    except Exception as e:
        print(f"Error during database test: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Testing database setup...")
    test_database_setup() 