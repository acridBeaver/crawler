from file_worker import *
from link_finder import LinkFinder
from yarl import URL


class Spider:
    project_name = ''
    domain_name = ''
    base_url = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name: str, domain_name: str, base_url: str):
        Spider.project_name = project_name
        Spider.domain_name = domain_name
        Spider.queue_file = self.project_name + '/queue.txt'
        Spider.crawled_file = self.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page(base_url)

    @staticmethod
    def boot():
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(url):
        link_finder = LinkFinder(Spider.domain_name, URL(url))
        link_finder.get_links()
        for link in link_finder.links:
            if link in Spider.crawled:
                continue
            Spider.queue.add(link)
        Spider.queue.remove(url)
        Spider.crawled.add(url)
        Spider.update_files()

    @staticmethod
    def update_files():
        try:
            set_to_file(Spider.queue_file, Spider.queue)
            set_to_file(Spider.crawled_file, Spider.crawled)
        except RuntimeError:
            Spider.update_files()

