import port
import software


class Asset:
    def __init__(self, hostname, os_info, open_ports, installed_software):
        self.hostname = hostname
        self.os_info = os_info
        self.open_ports = [port.port(p["port"], p["address"], p["pid"], p["process_name"]) for p in open_ports]
        self.installed_software = [software.Software(s["DisplayName"], s["DisplayVersion"], s["Publisher"], s["InstallDate"]) for s in installed_software]
        self.risk_score = 0  # Placeholder, can be calculated based on logic
        self.risk_notes = []  # Placeholder for any notes related to the risk assessment

    def to_dict(self):
        return {
            "hostname": self.hostname,
            "os_info": self.os_info,
            "open_ports": [p.to_dict() for p in self.open_ports],
            "installed_software": [s.to_dict() for s in self.installed_software],
            "risk_score": self.risk_score,
            "risk_notes": self.risk_notes
        }