from tuya.tuya_client import TuyaClient
import json

def main():
    try:
        # Initialize the client
        client = TuyaClient.get_client()
        
        # Your Tuya device ID
        device_id = "bfd049f7e821abbfd15sv9"
        
        # Get and print device information only
        print("\n=== Device Information ===")
        device_info = client.get_device_info(device_id)
        print(json.dumps(device_info, indent=2))
        
        # Removed the device status request to avoid double pulling

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 