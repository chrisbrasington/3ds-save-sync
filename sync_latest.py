import json
import os
import shutil
from ftplib import FTP, error_perm
from datetime import datetime

CONFIG_FILE = "config.json"
SAVE_PATH = "/3ds/Checkpoint/saves"
TMP_DIR = "./tmp"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def connect_ftp(host, port):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login('anonymous', 'anonymous@')
    return ftp

def list_games(ftp, filter_term):
    try:
        ftp.cwd(SAVE_PATH)
        games = []

        def parse_game_dir(line):
            parts = line.split()
            name = " ".join(parts[8:])
            if not filter_term or filter_term in name.lower():
                games.append(name)

        ftp.retrlines('LIST', parse_game_dir)
        return games
    except error_perm as e:
        print(f"[WARN] Unable to access '{SAVE_PATH}': {e}")
        return []

def get_latest_save(ftp, game_dir):
    full_path = f"{SAVE_PATH}/{game_dir}"
    try:
        parent_dir = '/'.join(full_path.split('/')[:-1])
        ftp.cwd(parent_dir)
        target_dir = full_path.split('/')[-1]

        directories = []
        for entry in ftp.mlsd():
            name, facts = entry
            if name == target_dir and facts['type'] == 'dir':
                ftp.cwd(name)
                for sub_entry in ftp.mlsd():
                    sub_name, sub_facts = sub_entry
                    if is_timestamp_folder(sub_name):
                        directories.append(sub_name)

        directories.sort(reverse=True)
        if directories:
            latest_save = f"{full_path}/{directories[0]}"
            print(f"[INFO] Found latest save: {latest_save}")
            return latest_save
        else:
            print(f"[WARN] No save found for '{game_dir}'. Skipping.")
            return None
    except error_perm as e:
        print(f"[WARN] Unable to access directory '{full_path}': {e}")
        return None

def is_timestamp_folder(folder_name):
    try:
        datetime.strptime(folder_name, "%Y%m%d-%H%M%S")
        return True
    except ValueError:
        return False


def ensure_directory_exists(ftp, device_name, path):
    """ Recursively create directories on the FTP server and log which device. """
    parts = path.split('/')
    for i in range(1, len(parts) + 1):
        directory = '/'.join(parts[:i])
        if not directory:  # Skip the root path
            continue
        try:
            ftp.cwd(directory)  # Try to change to the directory
        except error_perm:
            print(f"[INFO] Creating directory on {device_name}: {directory}")
            try:
                ftp.mkd(directory)  # Create it if it doesn't exist
            except error_perm as e:
                print(f"[ERROR] Failed to create directory '{directory}' on {device_name}: {e}")

def sync_save(source_ftp, target_ftp, source_name, target_name, source_path, target_path):
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    # Ensure the target directory exists before uploading files
    ensure_directory_exists(target_ftp, target_name, target_path)

    source_ftp.cwd(source_path)
    files = []
    source_ftp.retrlines('LIST', lambda line: files.append(line.split()[-1]))

    for file in files:
        local_tmp_file = os.path.join(TMP_DIR, file)
        # Download from source
        with open(local_tmp_file, 'wb') as f:
            source_ftp.retrbinary(f"RETR {file}", f.write)
        # Upload to target
        with open(local_tmp_file, 'rb') as f:
            target_ftp.storbinary(f"STOR " + os.path.join(target_path, file), f)

    print(f"[INFO] Synced from {source_name} {source_path} to {target_name} {target_path}")


def summarize_and_confirm(sync_plan, in_sync_games):
    print("\nSummary of actions:")
    for game, info in sync_plan.items():
        print(f"{game}: Copy from {info['source_name']} to {info['target_name']}")
    
    print("\nAlready in sync:")
    for game in in_sync_games:
        print(game)
    
    proceed = input("\nProceed with sync? (y/n): ").strip().lower()
    return proceed == 'y'

def main():
    # Ask for game filter
    game_filter = input("Enter game name to filter (leave empty to show all): ").strip().lower()

    # Load configuration
    config = load_config()

    # Establish FTP connections
    ftp_connections = {
        name: connect_ftp(details["ip"], details["port"]) 
        for name, details in config.items()
    }

    # Get the list of games and latest saves for each system
    saves = {}
    for name, ftp in ftp_connections.items():
        display_name = config[name]["display_name"]
        print(f"\n[INFO] Checking games on {display_name}...")
        
        games = list_games(ftp, game_filter)
        saves[name] = {}
        for game_path in games:
            latest_save = get_latest_save(ftp, game_path)
            if latest_save:
                game_name = game_path.replace(SAVE_PATH + '/', '')
                saves[name][game_name] = latest_save
                print(f"[INFO] Found latest save for {game_name}: {latest_save}")

    # Determine sync plan
    sync_plan = {}
    in_sync_games = []
    for game in set(g for s in saves.values() for g in s):
        latest = {}
        for system, game_saves in saves.items():
            if game in game_saves:
                latest[system] = game_saves[game]

        if len(latest) == 1:
            source = next(iter(latest.items()))
            target = [s for s in saves if s != source[0]][0]
            sync_plan[game] = {
                'source': source[0], 
                'target': target, 
                'save': source[1],
                'source_name': config[source[0]]['display_name'],
                'target_name': config[target]['display_name']
            }
        elif len(latest) == 2:
            sys1, sys2 = list(latest.keys())
            if latest[sys1] > latest[sys2]:
                sync_plan[game] = {
                    'source': sys1, 
                    'target': sys2, 
                    'save': latest[sys1],
                    'source_name': config[sys1]['display_name'],
                    'target_name': config[sys2]['display_name']
                }
            elif latest[sys2] > latest[sys1]:
                sync_plan[game] = {
                    'source': sys2, 
                    'target': sys1, 
                    'save': latest[sys2],
                    'source_name': config[sys2]['display_name'],
                    'target_name': config[sys1]['display_name']
                }
            else:
                # Both have the same latest save
                in_sync_games.append(game)

    # Confirm and execute sync
    if summarize_and_confirm(sync_plan, in_sync_games):
        for game, info in sync_plan.items():
            source_ftp = ftp_connections[info['source']]
            target_ftp = ftp_connections[info['target']]
            sync_save(source_ftp, target_ftp, info['save'], info['save'])

    # Clean up FTP connections and temp files
    for ftp in ftp_connections.values():
        ftp.quit()
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)

if __name__ == "__main__":
    main()
