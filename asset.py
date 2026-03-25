class Asset:
    def __init__(self, hostname, os_info, open_ports, installed_software):
        self.hostname = hostname
        self.os_info = os_info
        self.open_ports = open_ports
        self.installed_software = installed_software

    def to_dict(self):
        return {
            "hostname": self.hostname,
            "os_info": self.os_info,
            "open_ports": self.open_ports,
            "installed_software": self.installed_software
        }