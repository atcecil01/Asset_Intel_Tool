import json
import os
from asset import Asset

class AssetManager:
    def __init__(self):
        self.assets: list[Asset] = []

    def add_assets(self, file_path: str):
        self.assets.clear()  # Clear existing assets before adding new ones

        #Check if file_path is a directory, if so, iterate through all json files in the directory
        if os.path.isdir(file_path):
            for filename in os.listdir(file_path):
                if filename.endswith(".json"):
                    self._add_asset_from_file(os.path.join(file_path, filename))
        elif os.path.isfile(file_path):
            self._add_asset_from_file(file_path)

    def _add_asset_from_file(self, file_path: str):
        # Check if the file is a JSON file        
        if not file_path.endswith(".json"):
            print(f"Skipping non-JSON file: {file_path}")
            return

        with open(file_path, "r") as f:
            asset_data = json.load(f)
            hostname = asset_data.get("hostname")
            os_info = asset_data.get("os_info")
            open_ports = asset_data.get("open_ports")
            installed_software = asset_data.get("installed_software")
        self.assets.append(Asset(hostname, os_info, open_ports, installed_software))
    
    # def get_inventory(self, hostname):
    #     for asset in self.assets:
    #         if asset.hostname == hostname:
    #             return asset
    #     return None

    # def save_all_inventories(self):
    #     for hostname, inventory in self.assets.items():
    #         save_inventory_to_json(inventory, f"inventory_{hostname}.json")