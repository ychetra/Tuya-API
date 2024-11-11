import sys
import os
from datetime import datetime
import time

# Add the root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from database.db_utils import get_db_connection

def get_last_n_status(n=2, device_id=None):
    """Get last n status records for each device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if device_id:
            # For specific device
            cursor.execute('''
                SELECT TOP (?)
                    d.name as device_name,
                    d.device_id,
                    ds.timestamp,
                    ds.switch_1,
                    CASE 
                        WHEN ds.switch_1 = 1 THEN 'ON'
                        WHEN ds.switch_1 = 0 THEN 'OFF'
                        ELSE 'UNKNOWN'
                    END as status
                FROM device_status ds
                JOIN devices d ON d.device_id = ds.device_id
                WHERE ds.device_id = ?
                ORDER BY ds.timestamp DESC
            ''', (n, device_id))
        else:
            # For all devices, get last n records for each device
            cursor.execute('''
                WITH RankedStatus AS (
                    SELECT 
                        d.name as device_name,
                        d.device_id,
                        ds.timestamp,
                        ds.switch_1,
                        CASE 
                            WHEN ds.switch_1 = 1 THEN 'ON'
                            WHEN ds.switch_1 = 0 THEN 'OFF'
                            ELSE 'UNKNOWN'
                        END as status,
                        ROW_NUMBER() OVER (PARTITION BY d.device_id ORDER BY ds.timestamp DESC) as rn
                    FROM device_status ds
                    JOIN devices d ON d.device_id = ds.device_id
                )
                SELECT 
                    device_name,
                    device_id,
                    timestamp,
                    switch_1,
                    status
                FROM RankedStatus
                WHERE rn <= ?
                ORDER BY device_id, timestamp DESC
            ''', (n,))
        
        results = cursor.fetchall()
        
        if not results:
            print("No switch status data found")
            return
        
        print("\nLast Switch Status Records:")
        print("-" * 80)
        print(f"{'Device Name':<20} {'Device ID':<25} {'Timestamp':<25} {'Status':<10}")
        print("-" * 80)
        
        current_device = None
        for row in results:
            # Add a blank line between different devices
            if current_device and current_device != row[1]:
                print()
            current_device = row[1]
            
            try:
                timestamp = datetime.fromtimestamp(row[2])
                print(f"{row[0]:<20} {row[1]:<25} {timestamp.strftime('%Y-%m-%d %H:%M:%S'):<25} {row[4]:<10}")
            except Exception as e:
                print(f"{row[0]:<20} {row[1]:<25} {'Invalid timestamp':<25} {row[4]:<10}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def get_latest_switch_status(device_id=None):
    """Get latest status (shortcut to get_last_n_status with n=1)"""
    get_last_n_status(1, device_id)

if __name__ == "__main__":
    print("Getting last 2 status records for all devices...")
    get_last_n_status(2)
    
    # Example for specific device
    # device_id = "bfd049f7e821abbfd15sv9"
    # print(f"\nGetting last 2 status records for device {device_id}...")
    # get_last_n_status(2, device_id)