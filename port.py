class port:
    def __init__(self, port: int, address: str, pid: int, process: str):
        self.port = port
        self.address = address
        self.pid = pid
        self.process = process

    def to_dict(self):
        return {
            "port": self.port,
            "address": self.address,
            "pid": self.pid,
            "process": self.process
        }