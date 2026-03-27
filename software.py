class Software:
    def __init__(self, display_name: str, display_version: str, publisher: str, install_date):
        self.display_name = display_name
        self.display_version = display_version
        self.publisher = publisher
        self.install_date = install_date

    def to_dict(self):
        return {
            "DisplayName": self.display_name,
            "DisplayVersion": self.display_version,
            "Publisher": self.publisher,
            "InstallDate": self.install_date
        }