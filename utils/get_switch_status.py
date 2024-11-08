import sys
import os
from datetime import datetime
import time

# Add the root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from database.db_utils import get_db_connection

def get_switch_status(hours=24, device_id=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate the timestamp for hours ago
        current_time = int(time.time())
        hours_ago = current_time - (hours * 3600)  # Convert hours to seconds
        
        # Query to get switch_1 status history
        if device_id:
            # For specific device
            cursor.execute('''
                SELECT 
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
                WHERE ds.timestamp >= ? AND ds.device_id = ?
                ORDER BY ds.timestamp DESC
            ''', (hours_ago, device_id))
        else:
            # For all devices
            cursor.execute('''
                SELECT 
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
                WHERE ds.timestamp >= ?
                ORDER BY d.device_id, ds.timestamp DESC
            ''', (hours_ago,))
        
        results = cursor.fetchall()
        
        if not results:
            print("No switch status data found for the specified time period")
            return
        
        print("\nSwitch 1 Status History:")
        print("-" * 80)
        print(f"{'Device Name':<20} {'Device ID':<25} {'Timestamp':<25} {'Status':<10}")
        print("-" * 80)
        
        for row in results:
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get the latest switch_1 status
        if device_id:
            # For specific device
            cursor.execute('''
                SELECT TOP 1
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
            ''', (device_id,))
        else:
            # For all devices (latest status for each device)
            cursor.execute('''
                WITH LatestStatus AS (
                    SELECT 
                        device_id,
                        MAX(timestamp) as max_timestamp
                    FROM device_status
                    GROUP BY device_id
                )
                SELECT
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
                JOIN LatestStatus ls ON ds.device_id = ls.device_id AND ds.timestamp = ls.max_timestamp
                ORDER BY d.name
            ''')
        
        results = cursor.fetchall()
        
        if not results:
            print("No switch status data found")
            return
            
        print("\nCurrent Switch 1 Status:")
        print("-" * 80)
        
        for result in results:
            try:
                timestamp = datetime.fromtimestamp(result[2])
                print("-" * 80)
                print(f"Device Name: {result[0]}")
                print(f"Device ID: {result[1]}")
                print(f"Status: {result[4]}")
                print(f"Raw Switch Value: {result[3]}")
                print(f"Last Updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print("-" * 80)
                print(f"Device Name: {result[0]}")
                print(f"Device ID: {result[1]}")
                print(f"Status: {result[4]}")
                print(f"Raw Switch Value: {result[3]}")
                print("Last Updated: Invalid timestamp")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Getting current switch 1 status for all devices...")
    get_latest_switch_status()
    
    print("\nGetting switch 1 history for all devices (last 24 hours)...")
    get_switch_status(24)
    
    # Example for specific device
    # device_id = "bfd049f7e821abbfd15sv9"
    # print(f"\nGetting status for specific device {device_id}...")
    # get_latest_switch_status(device_id)
    # get_switch_status(24, device_id)