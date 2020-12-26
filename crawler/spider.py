import queue
import os
import logging
import requests

from pathlib import Path
from multiprocessing import Queue
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
from yarl import URL

from crawler.robotstxt_parser import RobotsTxtParser
from crawler.errors import CrawlerError, CantOpenLinkError


class Spider:

    def __init__(
        self,
        base_domain: str,
        domains: set[str],
        base_url: URL,
        directory: str,
        deep: int,
        save: bool,
        pool_count: int,
        disallow_ends: tuple
    ):
        self.scheme = base_url.scheme
        self.base_domain = base_domain
        self.domains = domains
        self.queue = Queue()
        self.crawled = []
        self.working_links = set()
        self.disallow_ends = disallow_ends
        self.directory = directory + "/"
        self.save = save
        self.deep = deep
        self.count = 0

        self.pool = ThreadPool(pool_count)

        self.robots_parser = RobotsTxtParser(base_url.human_repr())
        try:
            self.robots_parser.get_robots_txt()
        except CrawlerError as e:
            logging.warning(f"-RobotsTxT {e.message}")
            self.robots_parser.death = True
        self.crawl_page(base_url.human_repr())

    def crawl_page(self, link):
        self.count += 1
        self.deep -= 1
        logging.info(str(self.count) + ")crawling: " + link)
        self.working_links.add(link)
        self.crawled.append(link)
        new_links = self.get_links(URL(link))
        self.check_new_links(new_links)

    def check_new_links(self, links):
        for link in links:
            if link in self.working_links:
                continue
            if self.robots_parser.cant_fetch(link):
                continue
            self.working_links.add(link)
            self.queue.put(link)

    def get_links(self, url: URL) -> set:
        site_info = self.get_content(url.human_repr())
        if site_info.status_code != 200:
            logging.warning(
                f"{site_info.status_code} status code in get_links"
                f"({url.human_repr()})"
            )
            return set()
        html = site_info.text
        if self.save:
            path = Path.cwd() / self.directory / url.host
            FileWorker.save_link(path, url, html)
        return self.find_links(html, url)

    def find_links(self, html: str, url: URL) -> set:
        result = set()
        host_name = str(url.origin())
        soup = BeautifulSoup(html, "html.parser")
        for obj in soup.find_all("a", href=True):
            link = obj["href"].lower()
            if link.endswith(self.disallow_ends) or link.startswith("#"):
                continue
            link = URL(link)
            if self.check_domains(link) and link.human_repr().startswith(
                url.scheme
            ):
                result.add(self.get_normal_link(link))
            elif link.scheme == "":
                if not link.human_repr().startswith("/"):
                    result.add(url.human_repr() + link.human_repr())
                else:
                    result.add(host_name + link.human_repr())
        return result

    def check_domains(self, link: URL) -> bool:
        for domain in self.domains:
            if domain in link.human_repr():
                return True
        return False

    @staticmethod
    def get_normal_link(url: URL) -> str:
        return str(
            url.build(
                scheme=url.scheme,
                host=url.host,
                path=url.path,
                query=url.query,
            )
        )

    @staticmethod
    def get_content(link):
        try:
            result = requests.get(link)
        except Exception as e:
            logging.warning(
                f"Can`t connect to {link}"
                f"\nin Spider.get_content({link})"
                f"\n{type(e)}: {str(e)}"
            )
            raise CantOpenLinkError
        return result

    def start(self):
        while self.deep > 0:
            try:
                url = self.queue.get(timeout=10)
            except queue.Empty:
                break
            try:
                self.pool.apply_async(self.crawl_page, (url,))
            except CrawlerError as e:
                logging.warning(e.message)


class FileWorker:
    @staticmethod
    def create_project_dir(dir_name: str, folders: set):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        for folder in folders:
            deep_dir = f"{dir_name}/{folder}"
            if not os.path.exists(deep_dir):
                os.mkdir(deep_dir)

    @staticmethod
    def save_link(path, url: URL, html: str):
        if not path.is_dir():
            path.mkdir()
        if len(url.path) > 1:
            part_link = ''
            for part_link in url.path.rsplit('/'):
                path = path / part_link
                if not path.is_dir():
                    path.mkdir()
            path = path/part_link
        else:
            path = path / url.host
        FileWorker.write_file(path.with_suffix('.txt'), html)

    @staticmethod
    def write_file(path, data: str):
        with open(path, "w") as file:
            file.write(data)

    @staticmethod
    def file_to_set(file_name) -> set:
        result = set()
        with open(file_name, "rt") as text:
            for line in text:
                result.add(line.replace("\n", ""))
        return result

    @staticmethod
    def set_to_file(file_name, urls_set: set):
        with open(file_name, "w") as file:
            for url in urls_set:
                file.write(url + "\n")
