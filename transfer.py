import json
from ftplib import FTP
from datetime import datetime

CONFIG_FILE = "config.json"
SAVE_PATH = "/3ds/Checkpoint/saves"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def connect_ftp(host, port):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login('anonymous', 'anonymous@')
    return ftp

def list_folders(ftp, path):
    ftp.cwd(path)
    folders = []
    def parse_line(line):
        # Split the line and get the last part as the folder name
        parts = line.split(maxsplit=8)
        if len(parts) == 9:
            folder_name = parts[-1]
            folders.append(folder_name)  # Store just the folder name
    ftp.retrlines('LIST', parse_line)
    return folders

def get_latest_folder(ftp, path):
    ftp.cwd(path)
    folders = []
    ftp.retrlines('LIST', lambda line: folders.append(line.split()[-1]))
    # Filter folders that look like timestamps
    timestamp_folders = [f for f in folders if is_timestamp_folder(f)]
    if not timestamp_folders:
        print("No timestamped folders found.")
        exit(1)
    latest_folder = max(timestamp_folders, key=lambda f: datetime.strptime(f, "%Y%m%d-%H%M%S"))
    return latest_folder

def is_timestamp_folder(folder_name):
    try:
        datetime.strptime(folder_name, "%Y%m%d-%H%M%S")
        return True
    except ValueError:
        return False

def move_folder(source_ftp, target_ftp, source_path, target_path):
    source_ftp.cwd(source_path)
    target_ftp.cwd(target_path)
    
    files = []
    source_ftp.retrlines('LIST', lambda line: files.append(line.split()[-1]))

    for file in files:
        print(f"Transferring: {file}")
        with open(file, 'wb') as f:
            source_ftp.retrbinary(f"RETR {file}", f.write)
        with open(file, 'rb') as f:
            target_ftp.storbinary(f"STOR {file}", f)
    
    print(f"Moved latest folder from {source_path} to {target_path}")

def select_3ds_system(config, prompt):
    print(prompt)
    choices = list(config.items())
    for index, (name, details) in enumerate(choices, start=1):
        print(f"{index}. {name} ({details['display_name']})")
    choice = int(input("Enter number: "))
    
    # Check for valid choice
    if choice < 1 or choice > len(choices):
        print("Invalid choice. Exiting.")
        exit(1)
    
    selected_key, selected_value = choices[choice - 1]
    return selected_key, selected_value

def main():
    config = load_config()

    # Check if only two systems are available
    if len(config) == 2:
        # Automatically set one as source and the other as target
        items = list(config.items())
        source_key, source = items[0]
        target_key, target = items[1]

        print(f"Source automatically set to: {source['display_name']} ({source['ip']})")
        print(f"Target automatically set to: {target['display_name']} ({target['ip']})")
    else:
        # Manual selection
        source_key, source = select_3ds_system(config, "Select source 3DS:")
        target_config = {k: v for k, v in config.items() if k != source_key}
        
        if not target_config:
            print("No other systems available for target.")
            exit(1)

        target_key, target = select_3ds_system(target_config, "Select target 3DS:")

    print(f"Connecting to source: {source['display_name']} ({source['ip']})")
    source_ftp = connect_ftp(source['ip'], source['port'])
    print(f"Connecting to target: {target['display_name']} ({target['ip']})")
    target_ftp = connect_ftp(target['ip'], target['port'])

    # List folders in /3ds/Checkpoint/saves
    folders = list_folders(source_ftp, SAVE_PATH)
    print("Available folders:")
    for index, folder in enumerate(folders, start=1):
        print(f"{index}. {folder}")

    choice = int(input("Select a folder: "))
    if choice < 1 or choice > len(folders):
        print("Invalid folder choice. Exiting.")
        exit(1)

    chosen_folder = folders[choice - 1]
    latest_folder = get_latest_folder(source_ftp, f"{SAVE_PATH}/{chosen_folder}")
    source_path = f"{SAVE_PATH}/{chosen_folder}/{latest_folder}"
    target_path = f"{SAVE_PATH}/{chosen_folder}"
    
    # Ensure target directory exists
    try:
        target_ftp.cwd(target_path)
    except:
        print(f"Creating target directory: {target_path}")
        target_ftp.mkd(target_path)
        target_ftp.cwd(target_path)

    # Move the latest folder to the target 3DS
    move_folder(source_ftp, target_ftp, source_path, target_path)

    source_ftp.quit()
    target_ftp.quit()

if __name__ == "__main__":
    main()
