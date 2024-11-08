from database.db_utils import get_db_connection

def create_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create devices table
        cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'devices')
        BEGIN
            CREATE TABLE devices (
                id INT IDENTITY(1,1) PRIMARY KEY,
                device_id VARCHAR(255) UNIQUE,
                name VARCHAR(255),
                category VARCHAR(255),
                online BIT,
                active_time BIGINT,
                create_time BIGINT,
                update_time BIGINT,
                ip VARCHAR(255),
                model VARCHAR(255),
                time_zone VARCHAR(255)
            )
        END
        ''')

        # Modified device_status table to only include switch_1
        cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'device_status')
        BEGIN
            CREATE TABLE device_status (
                id INT IDENTITY(1,1) PRIMARY KEY,
                device_id VARCHAR(255),
                timestamp BIGINT,
                switch_1 BIT,
                CONSTRAINT FK_device_status_devices FOREIGN KEY (device_id) 
                    REFERENCES devices(device_id)
            )
        END
        ''')

        conn.commit()
        print("Database tables created successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_tables() 