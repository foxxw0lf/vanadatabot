import json
import time
from urllib.parse import parse_qs
from datetime import datetime
from colorama import Fore, init

# Initialize Colorama
init(autoreset=True)

# Function to read JSON file
def read_json_file(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] {Fore.WHITE}File {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}[ERROR] {Fore.WHITE}Failed to decode JSON from the file.")
        return None

# Function to extract authentication date and account ID from init data
def extract_auth_data_and_id(init_data):
    try:
        query = parse_qs(init_data)
        auth_date = int(query.get('auth_date', [0])[0])
        user_data = query.get('user', [])[0]
        user_json = json.loads(user_data)
        account_id = user_json.get('id', 'N/A')
        return auth_date, account_id
    except Exception as e:
        print(f'{Fore.RED}[ERROR] Failed to extract auth data or account ID: {e}')
        return None, 'N/A'

# Function to check if the data has expired
def is_data_expired(auth_date, current_timestamp, expiration_seconds=600):
    if auth_date:
        # Check if the data is older than the expiration time
        return (current_timestamp - auth_date) > expiration_seconds
    return True

# Function to handle expired data
def handle_expired_data(account_id):
    print(f'{Fore.YELLOW}[INFO] Authentication data for Account {account_id} has expired. Please re-authenticate.')

# Function to process accounts
def process_accounts(accounts):
    for data in accounts:
        init_data = data.get('x_telegram_web_app_init_data')
        if not init_data:
            print(f'{Fore.RED}[ERROR] x_telegram_web_app_init_data missing in account data.')
            continue

        auth_date, account_id = extract_auth_data_and_id(init_data)
        current_timestamp = int(time.time())
        
        if is_data_expired(auth_date, current_timestamp):
            handle_expired_data(account_id)
        else:
            print(f'{Fore.GREEN}[INFO] Authentication data for Account {account_id} is valid.')

def main():
    # Read account data from accounts.json
    accounts = read_json_file('accounts.json')
    if not accounts:
        exit(1)

    # Process each account
    process_accounts(accounts)

if __name__ == "__main__":
    main()
