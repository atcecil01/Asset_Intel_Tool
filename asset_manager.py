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
            nmap_ports = asset_data.get("nmap_ports")

        self.assets.append(Asset(hostname, os_info, open_ports, installed_software, nmap_ports))

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
        with open("config.json", "r") as f:
            config = json.load(f)
        high_risk_ports = {int(k): v for k, v in config["high_risk_ports"].items()}
        thresholds = config["thresholds"]
        risk_levels = config["risk_score_levels"]
        
        for asset in self.assets:
            risk_score = 0
            if len(asset.open_ports) > thresholds["open_ports"]:
                risk_score += 2
                asset.risk_notes.append("High number of open ports")
            for p in asset.open_ports:
                if p.port in high_risk_ports:
                    risk_score += high_risk_ports[p.port]
                    asset.risk_notes.append(f"Port {p.port} open")
            if len(asset.installed_software) > thresholds["installed_software"]:
                risk_score += 1
                asset.risk_notes.append("High number of installed software")
            if len(asset.open_ports) == 0 or len(asset.installed_software) == 0:
                risk_score += 2
                asset.risk_notes.append("No open ports or installed software")

            if risk_score <= risk_levels["low"]:
                asset.risk_score = "Low"
            elif risk_score <= risk_levels["medium"]:
                asset.risk_score = "Medium"
            elif risk_score <= risk_levels["high"]:
                asset.risk_score = "High"
            else:
                asset.risk_score = "Critical"

        return self.assets
    
    def advanced_risk_assessment(self):
        for asset in self.assets:
            risk_score = 0
            vuln_id = None
            for p in asset.nmap_ports:
                for v in p.vulnerabilities:
                    if v.cvss_score > risk_score:
                        risk_score = v.cvss_score
                        vuln_id = v.id
            if vuln_id:
                asset.risk_notes.append(f"Vulnerability {vuln_id} with CVSS score {risk_score} on port {p.portid}")
            asset.risk_score = risk_score
        return self.assets
