class reference:
    def __init__(self, url: str):
        self.url = url

    def to_dict(self):
        return {
            "url": self.url
        }