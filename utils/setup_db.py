import sys
import os
from dotenv import load_dotenv

# Add the root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from database.create_database import create_database
from database.drop_tables import drop_tables
from database.create_tables import create_tables
from database.test_database import test_database_setup

def setup_database():
    """
    Set up the entire database structure for new users.
    This will:
    1. Create the database if it doesn't exist
    2. Drop existing tables if they exist
    3. Create new tables
    4. Test the database setup
    """
    try:
        print("\n=== Starting Database Setup ===")
        
        print("\n1. Creating database...")
        create_database()
        
        print("\n2. Dropping existing tables if any...")
        drop_tables()
        
        print("\n3. Creating new tables...")
        create_tables()
        
        print("\n4. Testing database setup...")
        test_database_setup()
        
        print("\n=== Database Setup Completed Successfully ===")
        print("\nYou can now run 'python -m utils.store_device_data' to start monitoring devices")
        
    except Exception as e:
        print(f"\n❌ Error during database setup: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure SQL Server is running")
        print("2. Check your .env file configuration")
        print("3. Verify you have proper SQL Server permissions")
        print("4. Make sure no other applications are using the database")
        sys.exit(1)

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists(os.path.join(root_dir, '.env')):
        print("\n❌ Error: .env file not found!")
        print("Please create a .env file with your database configuration.")
        print("You can copy from .env.example if it exists.")
        sys.exit(1)
        
    # Load environment variables
    load_dotenv()
    
    # Confirm before proceeding
    print("\n⚠️  Warning: This will reset any existing database and tables!")
    response = input("Do you want to continue? (y/N): ")
    
    if response.lower() == 'y':
        setup_database()
    else:
        print("\nDatabase setup cancelled.")
        sys.exit(0) 