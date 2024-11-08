from test_device import TuyaClient
from database.db_utils import get_db_connection
import json
import time

# List of device IDs to monitor
DEVICE_IDS = [
    "bfd049f7e821abbfd15sv9",  # Device 1
    # "",    # Device 2
   
]

def get_current_status(client, device_id):
    """Get current device status and return switch states"""
    try:
        device_info = client.get_device_info(device_id)
        if device_info.get('success'):
            device_data = device_info['result']
            status_list = device_data.get('status', [])
            status_dict = {item.get('code'): item.get('value') for item in status_list}
            
            # Extract only switch_1 state
            switch_state = 1 if status_dict.get('switch_1') == True else 0
            return device_data, switch_state
    except Exception as e:
        print(f"Error getting device status for device {device_id}: {e}")
    return None, None

def get_last_stored_status(device_id):
    """Get the last stored switch state from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT TOP 1 switch_1, timestamp
            FROM device_status 
            WHERE device_id = ?
            ORDER BY timestamp DESC
        ''', (device_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'switch_1': result[0],
                'timestamp': result[1]
            }
    except Exception as e:
        print(f"Error getting last stored status for device {device_id}: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return None

def store_device_data(interval=5):
    try:
        client = TuyaClient.get_client()
        
        # Dictionary to store last known states for each device
        last_stored_states = {}
        
        print(f"Starting device monitoring (checking every {interval} seconds)...")
        print(f"Monitoring {len(DEVICE_IDS)} devices...")
        print("Press Ctrl+C to stop")
        
        # Initialize last stored states for all devices
        for device_id in DEVICE_IDS:
            last_stored = get_last_stored_status(device_id)
            last_stored_states[device_id] = last_stored['switch_1'] if last_stored else None
        
        while True:
            for device_id in DEVICE_IDS:
                device_data, current_state = get_current_status(client, device_id)
                
                if device_data is None:
                    print(f"\nFailed to get status for device {device_id}, skipping...")
                    continue
                
                # Only proceed if status has changed from last stored status
                if current_state != last_stored_states[device_id]:
                    print(f"\nSwitch 1 state change detected for device {device_id}!")
                    print(f"Previous state in DB: {'ON' if last_stored_states[device_id] == 1 else 'OFF'}")
                    print(f"Current state from API: {'ON' if current_state == 1 else 'OFF'}")
                    
                    # Connect to database
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    try:
                        # First, verify again that the status hasn't changed in the DB
                        latest_status = get_last_stored_status(device_id)
                        if latest_status and latest_status['switch_1'] == current_state:
                            print(f"Status already updated in database for device {device_id}, skipping...")
                            last_stored_states[device_id] = current_state
                            continue
                        
                        # Update or insert device information
                        cursor.execute('''
                        MERGE devices AS target
                        USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS source 
                        (device_id, name, category, online, active_time, create_time, update_time, ip, model, time_zone)
                        ON target.device_id = source.device_id
                        WHEN MATCHED THEN
                            UPDATE SET 
                                name = source.name,
                                category = source.category,
                                online = source.online,
                                active_time = source.active_time,
                                create_time = source.create_time,
                                update_time = source.update_time,
                                ip = source.ip,
                                model = source.model,
                                time_zone = source.time_zone
                        WHEN NOT MATCHED THEN
                            INSERT (device_id, name, category, online, active_time, create_time, update_time, ip, model, time_zone)
                            VALUES (source.device_id, source.name, source.category, source.online, source.active_time, 
                                    source.create_time, source.update_time, source.ip, source.model, source.time_zone);
                        ''', (
                            device_data.get('id'),
                            device_data.get('name'),
                            device_data.get('category'),
                            device_data.get('online'),
                            device_data.get('active_time'),
                            device_data.get('create_time'),
                            device_data.get('update_time'),
                            device_data.get('ip'),
                            device_data.get('model'),
                            device_data.get('time_zone')
                        ))
                        
                        # Store new device status
                        cursor.execute('''
                        INSERT INTO device_status (device_id, timestamp, switch_1)
                        VALUES (?, ?, ?)
                        ''', (
                            device_id,
                            int(time.time()),
                            current_state
                        ))
                        
                        conn.commit()
                        print(f"New status stored successfully for device {device_id}!")
                        last_stored_states[device_id] = current_state
                        
                    except Exception as e:
                        print(f"Error storing data for device {device_id}: {e}")
                        conn.rollback()
                    finally:
                        conn.close()
                else:
                    print(".", end="", flush=True)  # Progress indicator
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    store_device_data(interval=5)  # Check every 5 seconds