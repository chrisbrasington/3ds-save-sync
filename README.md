### sync_latest.py  

This script connects to two 3DS systems via FTP, automatically determines which system has the latest save file, and transfers it to the other system.  

### Features:  
- Connects to two 3DS devices over FTP.  
- Scans both systems for the most recent save file.  
- Automatically determines the source (newer save) and target (older save).  
- Transfers the latest save file from source to target.  

### How It Works:  
- The script searches in the `/3ds/Checkpoint/saves` directory on both systems.  
- It compares the modification dates of save files to identify the most recent one.  
- The system with the newest save is designated as the source.  
- The save file is then transferred to the target system, ensuring both devices are up to date.  

### Requirements:  
- Python 3.x (includes `ftplib` module)  

### Usage:  
```bash
python3 sync_latest.py
```