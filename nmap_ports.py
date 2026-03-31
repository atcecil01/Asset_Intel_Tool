from vulnerability import vulnerability

class nmap_port:
    def __init__(self, protocol: str, port: int, state: str, name: str, product: str, version: str, vulnerabilities):    
        self.protocol = protocol
        self.portid = port
        self.state = state
        self.name = name
        self.product = product
        self.version = version
        self.vulnerabilities = [vulnerability(v["id"], v["cvss_score"], v["references"]) for v in (vulnerabilities or [])]

    def to_dict(self):
        return {
            "protocol": self.protocol,
            "portid": self.portid,
            "state": self.state,
            "name": self.name,
            "product": self.product,
            "version": self.version,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities]
        }