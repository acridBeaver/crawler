from app.file_worker import *
from app.link_finder import LinkFinder
from yarl import URL
import threading


class Spider:
    queue = set()
    crawled = set()

    def __init__(self, project_name: str, domain_name: str, base_url: str):
        self.project_name = project_name
        self.domain_name = domain_name
        self.queue_file = self.project_name + '/queue.txt'
        self.crawled_file = self.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page(base_url)

    def boot(self):
        self.queue = file_to_set(self.queue_file)
        self.crawled = file_to_set(self.crawled_file)

    def crawl_page(self, url):
        link_finder = LinkFinder(self.domain_name, URL(url))
        link_finder.get_links()
        self.queue.update(self.check_new_links(link_finder.links))
        self.queue.remove(url)
        self.crawled.add(url)
        self.update_files()

    def check_new_links(self, links):
        result = set()
        for link in links:
            if link in self.crawled:
                continue
            result.add(link)
        return result

    def update_files(self):
        set_to_file(self.queue_file, self.queue)
        set_to_file(self.crawled_file, self.crawled)
