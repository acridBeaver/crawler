import requests

class RobotsTxtParser:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.allow_links = set()
        self.disallow_links = set()

    def make_sets(self):
