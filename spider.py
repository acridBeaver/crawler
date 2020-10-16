from file_worker import *
from link_finder import LinkFinder
from yarl import URL


class Spider:
    project_name = ''
    base_url = ''
    host_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name: str, base_url: str, host_name: str):
        self.project_name = project_name
        self.base_url = base_url
        self.host_name = host_name
        self.queue_file = self.project_name + '/queue.txt'
        self.crawled_file = self.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page()

    def boot(self):
        self.queue = file_to_set(self.queue_file)
        self.crawled = file_to_set(self.crawled_file)

    def crawl_page(self):
        url = self.queue.pop()
        link_finder = LinkFinder(self.base_url, self.host_name, URL(url))
        link_finder.get_links()
        for link in link_finder.links:
            if link in self.crawled:
                continue
            self.queue.add(link)
        self.crawled.add(url)
        self.update_files()

    def update_files(self):
        set_to_file(self.queue_file, self.queue)
        set_to_file(self.crawled_file, self.crawled)

