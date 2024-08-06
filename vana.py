import json
import requests
import random
import time
from colorama import Fore, init
from urllib.parse import parse_qs

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

# Function to extract user ID from x_telegram_web_app_init_data
def extract_user_id(init_data):
    try:
        query = parse_qs(init_data)
        user_json = query.get('user', [])[0]
        user_data = json.loads(user_json)
        return user_data.get('id', 'N/A')
    except Exception as e:
        print(f'{Fore.RED}[ERROR] Failed to extract user ID: {e}')
        return 'N/A'

# Function to send custom task points
def send_task_points(task_url, headers, min_points, max_points, account_id, sleep_duration):
    custom_points = random.randint(min_points, max_points)  # Generate random points within the range
    payload = {
        "points": custom_points
    }
    print(f'{Fore.BLUE}[INFO] [Account {account_id}] Sending {custom_points} points VANA.')
    response = requests.post(task_url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f'{Fore.GREEN}[INFO] [Account {account_id}] Successfully sent {custom_points} points VANA.')
    else:
        print(f'{Fore.RED}[ERROR] [Account {account_id}] Failed to send points. Status code: {response.status_code}')
        print(f'{Fore.RED}[ERROR] [Account {account_id}] Response: {response.text}')
        if response.status_code == 400:
            error_message = response.json().get("message", "")
            if "Points limit exceeded" in error_message:
                # Handle points limit exceeded by waiting sleep_duration from config.json
                print(f'{Fore.YELLOW}[INFO] [Account {account_id}] Points limit exceeded. Waiting for {sleep_duration} seconds as per config.')
                time.sleep(sleep_duration)

# Function to check points, send custom points, and get updated points
def check_points_and_send(login_url, task_url, headers, min_points, max_points, check_interval, loop_count, sleep_duration, account_id):
    loop_counter = 0
    while loop_counter < loop_count:
        try:
            # Send POST request for login
            response = requests.post(login_url, headers=headers, json={"id": account_id})
            if response.status_code == 200:
                response_json = response.json()
                print(f'{Fore.CYAN}[INFO] [Account {account_id}] ======================================')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] TELEGRAM ID: {response_json.get("id", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] USERNAME: {response_json.get("tgUsername", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] FIRST NAME: {response_json.get("tgFirstName", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] LAST NAME: {response_json.get("tgLastName", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] LANGUAGE: {response_json.get("tgLanguage", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] MULTIPLIER: {response_json.get("multiplier", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] TG WALLET ADDRESS: {response_json.get("tgWalletAddress", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] VANA WALLET ADDRESS: {response_json.get("vanaWalletAddress", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] CREATED AT: {response_json.get("createdAt", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] UPDATED AT: {response_json.get("updatedAt", "N/A")}')
                print(f'{Fore.GREEN}[INFO] [Account {account_id}] POINTS: {response_json.get("points", "N/A")}')
                
                # Fetch task data
                task_response = requests.get(task_url, headers=headers)
                if task_response.status_code == 200:
                    task_json = task_response.json()
                    task_points = task_json.get("points", 0)
                    print(f'{Fore.CYAN}[INFO] [Account {account_id}] ======================================')
                else:
                    print(f'{Fore.RED}[ERROR] [Account {account_id}] Failed to fetch task data with status code: {task_response.status_code}')
                    print(f'{Fore.RED}[ERROR] [Account {account_id}] Response: {task_response.text}')
                
                # Send custom task points
                send_task_points(task_url, headers, min_points, max_points, account_id, sleep_duration)
                
                # Get updated points after sending custom points
                response = requests.post(login_url, headers=headers, json={"id": account_id})
                if response.status_code == 200:
                    response_json = response.json()
                    updated_points = response_json.get("points", "N/A")
                    print(f'{Fore.GREEN}[INFO] [Account {account_id}] Updated POINTS: {updated_points}')
                else:
                    print(f'{Fore.RED}[ERROR] [Account {account_id}] Failed to fetch updated points. Status code: {response.status_code}')
                    print(f'{Fore.RED}[ERROR] [Account {account_id}] Response: {response.text}')
                
                # Wait before the next check
                print(f'{Fore.YELLOW}[INFO] [Account {account_id}] Waiting for {check_interval} seconds before the next send VANA Points...')
                time.sleep(check_interval)
                
                loop_counter += 1
            else:
                print(f'{Fore.RED}[ERROR] [Account {account_id}] Login tidak berhasil: {response.text}')
                break

        except requests.exceptions.RequestException as e:
            print(f'{Fore.RED}[ERROR] [Account {account_id}] Exception occurred: {e}')
            break  # Exit the loop on request exception

    # Wait for sleep_duration before proceeding to the next account
    print(f'{Fore.YELLOW}[INFO] [Account {account_id}] Completed {loop_count} loops. Waiting for {sleep_duration} seconds before switching to the next account...')
    time.sleep(sleep_duration)  # Sleep for the specified duration


def process_account(account_data, login_url, task_url, min_points, max_points, check_interval, loop_count, sleep_duration):
    init_data = account_data.get("x_telegram_web_app_init_data")
    if not init_data:
        print(f'{Fore.RED}[ERROR] x_telegram_web_app_init_data missing in account data.')
        return
    
    account_id = extract_user_id(init_data)
    if account_id == 'N/A':
        print(f'{Fore.RED}[ERROR] Failed to extract Account ID from x_telegram_web_app_init_data.')
        return

    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "priority": "u=1, i",
        "referer": "https://www.vanadatahero.com/home",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "x-telegram-web-app-init-data": init_data
    }
    check_points_and_send(
        login_url=login_url,
        task_url=task_url,
        headers=headers,
        min_points=min_points,
        max_points=max_points,
        check_interval=check_interval,
        loop_count=loop_count,
        sleep_duration=sleep_duration,
        account_id=account_id
    )

def main():
    hijau = Fore.GREEN
    putih = Fore.WHITE
    biru = Fore.BLUE
    merah = Fore.RED
    kuning = Fore.YELLOW
    banner = f"""
    {hijau}BOT VANADATAHERO{biru} 
    {hijau}Github : {putih}https://github.com/foxxw0lf
    {hijau}Telegram : {putih}https://t.me/anggastwn
    
    {kuning}User-owned AI through user-owned data. Backed by @paradigm @polychain{kuning}

    {merah}NOT FOR SALE! | DYOR | This BOT is FREE{merah}
    """
    
    print(banner)

    # Read account data from accounts.json
    accounts = read_json_file('accounts.json')
    if not accounts:
        exit(1)

    # Read configuration from config.json
    config = read_json_file('config.json')
    if not config:
        exit(1)

    min_points = config.get("custom_points_min", 100)  # Set default to 100 if not specified
    max_points = config.get("custom_points_max", 1000)  # Set default to 1000 if not specified
    check_interval = config.get("check_interval", 60)  # Set default to 60 seconds if not specified
    loop_count = config.get("loop_count", 10)  # Set default to 10 loops if not specified
    sleep_duration = config.get("sleep_duration", 3600)  # Set default to 1 hour if not specified
    account_switch_delay = config.get("account_switch_delay", 10)  # Delay between accounts

    # URLs for login and task
    login_url = "https://www.vanadatahero.com/api/player"
    task_url = "https://www.vanadatahero.com/api/tasks/1"

    # Process each account
    for i, account_data in enumerate(accounts):
        if i > 0:
            print(f'{Fore.YELLOW}[INFO] Waiting for {account_switch_delay} seconds before processing the next account...')
            time.sleep(account_switch_delay)  # Delay between processing different accounts
        
        process_account(
            account_data=account_data,
            login_url=login_url,
            task_url=task_url,
            min_points=min_points,
            max_points=max_points,
            check_interval=check_interval,
            loop_count=loop_count,
            sleep_duration=sleep_duration
        )

if __name__ == "__main__":
    main()
