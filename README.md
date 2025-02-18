### sync_latest.py  

This script connects to two 3DS systems via FTP, automatically determines which system has the latest save file, and transfers it to the other system.  

Using [checkpoint](https://github.com/BernardoGiordano/Checkpoint) save backups and (ftpd)[https://github.com/mtheall/ftpd]

### Steps:
1. Using [checkpoint](https://github.com/BernardoGiordano/Checkpoint), create a backup save on the source system.
2. Run (ftpd)[https://github.com/mtheall/ftpd] on the source system
3. Also run (ftpd)[https://github.com/mtheall/ftpd] on the target system
4. Ensure the config.json has the two systems
5. Run `python sync_latest.py`
6. Optionally use a search term (case insensitive)

The program will automatically determine with system has the latest backup per game, and per game will determine with 3DS is the target and which is the source.

7. `y` to PROCEED and saves will be copied between the systems.

8. On the target 3DS, use [checkpoint](https://github.com/BernardoGiordano/Checkpoint) to RESTORE the latest backup to device.

#### Caution:

It is possible that the Checkpoint backup is outdated if you have not created a backup recently.
While this program detects the "latest backup" it cannot know if it is older than the actual save of the game on the system.

Be intentional with your restore operation (possibly even creating a backup before a restore).

Additionally, some games like `Etrian Odyssey V` do not transfer SD-CARD backups (it seems) and only the primary backup in slot 1.

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

#### Sample run
```
python sync_latest.py 
Enter game name to filter (leave empty to show all): EO

[INFO] Checking games on red...
[DEBUG] Found games: ['/3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth']
navigating to /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth
[INFO] Found latest save: /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20250217-190744
[INFO] Found latest save for 0x01C51 EO V  Beyond the Myth: /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20250217-190744

[INFO] Checking games on small...
[DEBUG] Found games: ['/3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth']
navigating to /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth
[INFO] Found latest save: /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20250217-165254
[INFO] Found latest save for 0x01C51 EO V  Beyond the Myth: /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20250217-165254

Summary of actions:
0x01C51 EO V  Beyond the Myth: Copy from red to small

Already in sync:

Proceed with sync? (y/n): y
[INFO] Creating directory on small: /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20250217-190744
[INFO] Synced from red /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20250217-190744 to small /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20250217-190744
```