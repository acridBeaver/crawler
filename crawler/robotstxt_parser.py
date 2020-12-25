import requests
import logging
import re

from crawler.errors import RobotsTxtConnectionError
from crawler.errors import RobotsTxtNotFoundError


def process_link(links):
    for i in range(0, len(links)):
        link = links[i]
        if link == "/?" or link == "?":
            links[i] = "#"
            continue
        if not link.startswith("$"):
            link = f".+{link}"
        if not link.endswith("$"):
            link = f"{link}.+"
        links[i] = link.replace("$", "")


class RobotsTxtParser:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.death = False
        self.allow_links = []
        self.disallow_links = []

    def get_robots_txt(self):
        logging.info("getting RobotsTXT")
        try:
            doc = requests.get(f"{self.base_url}robots.txt")
        except Exception as e:
            self.death = True
            raise RobotsTxtConnectionError(e)
        if doc.status_code != 200:
            self.death = True
            logging.warning(f"site haven`t robots.txt - {doc.status_code}")
            raise RobotsTxtNotFoundError()
        self.make_sets(doc.text)

    def make_sets(self, doc):
        for fragment in doc.split("\n\n"):
            for line in fragment.split("\n"):
                if line.startswith("#"):
                    continue
                if line != "User-agent: *" and not line.startswith(
                    ("Disallow:", "Allow:")
                ):
                    break
                params = line.rsplit(" ", maxsplit=1)
                if params[0] == "Disallow:":
                    self.disallow_links.append(
                        params[1].strip().replace("*", ".+")
                    )
                if params[0] == "Allow:":
                    self.allow_links.append(
                        params[1].strip().replace("*", ".+")
                    )
        process_link(self.disallow_links)
        process_link(self.allow_links)

    def cant_fetch(self, link):
        if self.death:
            return False
        for disallow in self.disallow_links:
            if re.search(disallow, link):
                for allow in self.allow_links:
                    if re.search(allow, link):
                        return False
                return True
        return False
