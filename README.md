# 3DS Save Transfer Script

Easily transfer save files between two 3DS systems over FTP, preserving timestamped folder structures.

## Features
- Lists available save folders on the source 3DS.
- Automatically detects the latest timestamped save folder.
- Transfers the latest save folder to the target 3DS, maintaining subdirectory structure.
- Overwrite prompt if the save already exists on the target.

## Requirements
- Python 3.x
- FTP access enabled on both 3DS systems (e.g., using **FTPDB** or **FTPD**).
- `config.json` file for 3DS connection details.

## Configuration
Create a `config.json` file with the following structure:
```json
{
  "3ds1": {
    "display_name": "3DS Source",
    "ip": "192.168.1.100",
    "port": 21
  },
  "3ds2": {
    "display_name": "3DS Target",
    "ip": "192.168.1.101",
    "port": 21
  }
}
```

## Usage
```sh
python3 transfer.py
```

- Select the source 3DS.
- Confirm the target 3DS (auto-selected).
- Choose the game folder to transfer.
- The script will find the latest timestamped folder and transfer it.

## Example
```
Select source 3DS:
1. 3DS Source (192.168.1.100)
Enter number: 1
Target automatically set to: 3DS Target (192.168.1.101)
Connecting to source: 3DS Source (192.168.1.100)
Connecting to target: 3DS Target (192.168.1.101)
Available folders:
1. 0x01C51 EO V  Beyond the Myth
2. 0x01D21 Pokémon Sun
Select a folder: 1
Latest folder to transfer: /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20190622-130016
Transferring: data.bin
Moved latest folder from /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20190622-130016 to /3ds/Checkpoint/saves/0x01C51 EO V  Beyond the Myth/20190622-130016
```

## Notes
- Ensure both 3DS systems are on the same network.
- If the latest save folder already exists on the target, you'll be prompted to overwrite or skip.

## License
This project is open-source and available under the MIT License.

## Acknowledgments
Thanks to the 3DS homebrew community for making save management so accessible!
