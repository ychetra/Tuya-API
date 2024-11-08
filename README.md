# Tuya Device Status Monitor

A Python application that monitors Tuya smart devices and stores their switch status changes in a SQL Server database.

## Project Structure

```
project_root/
│
├── database/              # Database-related files
│   ├── __init__.py
│   ├── db_utils.py       # Database connection utilities
│   ├── create_database.py # Creates the database
│   ├── create_tables.py  # Creates required tables
│   ├── drop_tables.py    # Drops existing tables
│   └── test_database.py  # Tests database connectivity
│
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── store_device_data.py  # Monitors and stores device status
│   └── get_switch_status.py  # Retrieves device status history
│
├── tuya/                 # Tuya API related files
│   ├── __init__.py
│   ├── tuya_client.py          # Tuya API client
│   └── tuya_device.py         # Device-specific functions
│
└── .env                 # Configuration file
```

## Prerequisites
1. Python 3.7 or higher
2. SQL Server Express installed
3. Tuya IoT Platform account and device credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ychetra/Tuya-API
```

2. Install required packages:
```bash
pip install pyodbc python-dotenv tuyapy
```

3. Configure your `.env` file:
```env
# Tuya API Credentials
API_ENDPOINT="https://openapi.tuyaeu.com"
ACCESS_ID="your_access_id"
ACCESS_KEY="your_access_key"

# Database Configuration
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_SERVER=YOUR-PC\SQLEXPRESS
DB_NAME=tuya_db
DB_TRUSTED_CONNECTION=yes
```

## Setup

1. Create the database:
```bash
python -m database.create_database
```

2. Create tables:
```bash
python -m database.create_tables
```

3. Test database connection:
```bash
python -m database.test_database
```

## Configuration

1. Create a `devices.env` file in the project root:
```env
# Tuya API Credentials
API_ENDPOINT="https://openapi.tuyaeu.com"
ACCESS_ID="your_access_id"
ACCESS_KEY="your_access_key"

# Database Configuration
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_SERVER=YOUR-PC\SQLEXPRESS
DB_NAME=tuya_db
DB_TRUSTED_CONNECTION=yes
```

## Usage

1. Start monitoring devices:
```bash
python -m utils.store_device_data
```
This will continuously monitor your devices and store status changes in the database.

2. View device status history:
```bash
python -m utils.get_switch_status
```

### Available Commands

- Get latest status for all devices:
```python
from utils.get_switch_status import get_latest_switch_status
get_latest_switch_status()
```

- Get status history for specific device:
```python
from utils.get_switch_status import get_switch_status
get_switch_status(hours=24, device_id="your_device_id")
```

## Features

- Monitors multiple Tuya devices simultaneously
- Stores switch status changes in SQL Server database
- Only records when status actually changes
- Provides status history and current status queries
- Handles connection errors and retries

## Troubleshooting

1. Database Connection Issues:
   - Verify SQL Server is running
   - Check server name in .env file
   - Ensure SQL Server authentication is properly configured

2. Tuya API Issues:
   - Verify API credentials in .env file
   - Check device IDs are correct
   - Ensure devices are online and accessible

3. Import Errors:
   - Make sure you're running commands from project root
   - Verify all required packages are installed
   - Check Python path includes project root

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.