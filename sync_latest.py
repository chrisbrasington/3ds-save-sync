import json
import os
import shutil
import ftplib
from ftplib import FTP
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


def list_game_saves(ftp):
    ftp.cwd(SAVE_PATH)
    games = []
    ftp.retrlines('LIST', lambda line: games.append(line.split()[-1]))
    return games


def get_latest_save(ftp, game_dir):
    try:
        # Change to the base save path
        ftp.cwd(SAVE_PATH)
        
        # List directories in the base save path
        directories = ftp.nlst()
        for directory in directories:
            # Check if the directory name contains the game_dir
            if game_dir in directory:
                try:
                    # Change to the matched directory
                    ftp.cwd(directory)
                    
                    # List files and sort them alphabetically
                    files = ftp.nlst()
                    files.sort(reverse=True)  # Assuming latest file is last
                    
                    # Return the latest file with the correct path
                    if files:
                        latest_save = files[0]
                        full_path = f"{SAVE_PATH}/{directory}/{latest_save}"
                        return full_path
                except ftplib.error_perm as e:
                    print(f"[WARN] Unable to access directory '{SAVE_PATH}/{directory}': {e}")
                    
        print(f"[WARN] No save found for '{game_dir}'. Skipping.")
        return None
        
    except ftplib.error_perm as e:
        print(f"[ERROR] Unable to access base save path '{SAVE_PATH}': {e}")
        return None

def is_timestamp_folder(folder_name):
    try:
        datetime.strptime(folder_name, "%Y%m%d-%H%M%S")
        return True
    except ValueError:
        return False


def summarize_and_confirm(sync_plan):
    print("Summary of actions:")
    for game, info in sync_plan.items():
        print(f"{game}: Copy from {info['source']} to {info['target']}")
    proceed = input("Proceed with sync? (y/n): ").strip().lower()
    return proceed == 'y'


def sync_save(source_ftp, target_ftp, game_dir, latest_save):
    source_path = f"{SAVE_PATH}/{game_dir}/{latest_save}"
    target_path = f"{SAVE_PATH}/{game_dir}/{latest_save}"
    source_ftp.cwd(source_path)
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    files = []
    source_ftp.retrlines('LIST', lambda line: files.append(line.split()[-1]))

    for file in files:
        local_tmp_file = os.path.join(TMP_DIR, file)
        with open(local_tmp_file, 'wb') as f:
            source_ftp.retrbinary(f"RETR {file}", f.write)
        with open(local_tmp_file, 'rb') as f:
            target_ftp.storbinary(f"STOR {file}", f)


def main():
    config = load_config()
    systems = list(config.items())
    ftp_connections = {name: connect_ftp(info['ip'], info['port']) for name, info in systems}
    all_games = set()
    saves = {}

    for game, latest_save in saves[name].items():
        if latest_save:
            # Determine the direction
            direction = "n3ds -> n3dsxl" if name == "n3ds" else "n3dsxl -> n3ds"
            # Print the full path and direction
            print(f"{latest_save} - {direction}")

    sync_plan = {}
    for game in all_games:
        latest = {}
        for system, save_data in saves.items():
            if game in save_data and save_data[game]:
                latest[system] = save_data[game]

        if len(latest) == 1:
            source, latest_save = next(iter(latest.items()))
            target = [s for s in saves if s != source][0]
            sync_plan[game] = {'source': source, 'target': target, 'save': latest_save}
        elif len(latest) == 2:
            sys1, sys2 = list(latest.keys())
            if latest[sys1] > latest[sys2]:
                sync_plan[game] = {'source': sys1, 'target': sys2, 'save': latest[sys1]}
            elif latest[sys2] > latest[sys1]:
                sync_plan[game] = {'source': sys2, 'target': sys1, 'save': latest[sys2]}

    if summarize_and_confirm(sync_plan):
        for game, info in sync_plan.items():
            print(f"Syncing {game} from {info['source']} to {info['target']}")
            source_ftp = ftp_connections[info['source']]
            target_ftp = ftp_connections[info['target']]
            sync_save(source_ftp, target_ftp, game, info['save'])

    for ftp in ftp_connections.values():
        ftp.quit()

    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    main()
