import json
import os
from asset import Asset
from tabulate import tabulate

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
    
    def list_assets(self):
            table = []
            for asset in self.assets:
                table.append([asset.hostname, asset.os_info, len(asset.open_ports), len(asset.installed_software)])
            return tabulate(table, headers=["Hostname", "OS", "Open Ports", "Software Count"])
    
    def risky_hosts(self, advanced=False):
        if advanced:
            return self.advanced_risk_assessment()
        else:
            return self.basic_risk_assessment()

    def basic_risk_assessment(self):
        risk_score = 0
        
        for asset in self.assets:
            if len(asset.open_ports) > 10:
                risk_score += 2
                asset.risk_notes.append("High number of open ports")
            port_risks = {3389: 3, 22: 3, 445: 2}
            for p in asset.open_ports:
                if p.port in port_risks:
                    risk_score += port_risks[p.port]
                    asset.risk_notes.append(f"Port {p.port} open")
            if len(asset.installed_software) > 5:
                risk_score += 1
                asset.risk_notes.append("High number of installed software")
            if len(asset.open_ports) == 0 or len(asset.installed_software) == 0:
                risk_score += 2
                asset.risk_notes.append("No open ports or installed software")

            if risk_score <= 2:
                asset.risk_score = "Low"
            elif risk_score <= 5:
                asset.risk_score = "Medium"
            elif risk_score <= 8:
                asset.risk_score = "High"
            else:
                asset.risk_score = "Critical"

        return self.assets
    
    def advanced_risk_assessment(self):
        # TODO: Implement more advanced risk assessment logic based on specific software vulnerabilities, port risks, and other factors
        pass