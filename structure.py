import queue
from multiprocessing.pool import ThreadPool
from typing import List

import yarl


class Clawler:
    allowed_domains: List[str] = ["*.google.com", "drive.google.com"]

    unvisited_urls: queue.Queue = queue.Queue()
    visited_urls: set = set()

    pool = ThreadPool(10)

    def __init__(self):
        self.save_on_disk = False

    def fetch_page(self, url: str) -> str:
        return 'html'

    def extract_links(self, html: str) -> List[yarl.URL]:
        return [yarl.URL('link')]

    def crawl(self, url):
        html = self.fetch_page(url)
        self.visited_urls.add(url)
        links = self.extract_links(html)
        for link in links:
            if link in self.visited_urls:
                continue
            # проверка на валидность домена
            self.unvisited_urls.put(link)

    def start(self):
        while True:
            url = self.unvisited_urls.get()
            self.pool.apply_async(self.crawl, (url,))
