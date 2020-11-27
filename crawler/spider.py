from yarl import URL
from bs4 import BeautifulSoup
from multiprocessing import Queue
import queue
from crawler.robotstxt_parser import RobotsTxtParser
import crawler.file_worker as file_worker
from multiprocessing.pool import ThreadPool
import requests

DISALLOW_ENDS = ('.jpg', '.png', '.pptx', '.txt', 'xml')


class Spider:
    pool = ThreadPool(5)
    count = 0

    def __init__(self,
                 domain_name: str,
                 base_url: str,
                 robots_parser: RobotsTxtParser,
                 directory: str,
                 deep: int,
                 save: bool):
        self.scheme = URL(base_url).scheme
        self.domain_name = domain_name
        self.robots_parser = robots_parser
        self.queue = Queue()
        self.crawled = []
        self.working_links = set()
        self.directory = directory + '/'
        self.save = save
        self.deep = deep
        self.crawl_page(base_url)

    def crawl_page(self, link):
        self.count += 1
        self.deep -= 1
        print(str(self.count) + ')crawling: ' + link)
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
        site_info = self.get_content(str(url))
        if site_info is None or site_info.status_code != 200:
            return set()
        html = site_info.text
        if self.save:
            file_worker.write_file(self.directory + url.human_repr().replace('/', '') + '.txt', html)
        return self.find_links(html, url)

    @staticmethod
    def get_host_name(url: URL):
        return str(url.origin())

    def find_links(self, html: str, url: URL) -> set:
        result = set()
        host_name = self.get_host_name(url)
        soup = BeautifulSoup(html, 'html.parser')
        for obj in soup.find_all('a', href=True):
            link = obj['href']
            if link.endswith(DISALLOW_ENDS) or link.startswith('#'):
                continue
            link = URL(link)
            if self.domain_name in link.human_repr() and link.human_repr().startswith(url.scheme):
                result.add(self.get_normal_link(link))
            elif link.scheme == '':
                if not link.human_repr().startswith('/'):
                    result.add(url.human_repr() + link.human_repr())
                else:
                    result.add(host_name + link.human_repr())
        return result

    @staticmethod
    def get_normal_link(url: URL) -> str:
        return str(url.build(scheme=url.scheme, host=url.host, path=url.path, query=url.query))

    @staticmethod
    def get_content(link):
        try:
            result = requests.get(link)
        except Exception as e:
            print(f'{type(e)}: {str(e)} in Spider.get_content({link})')
            return None
        return result

    def start(self):
        while self.deep > 0:
            try:
                url = self.queue.get(timeout=10)
            except queue.Empty:
                break
            self.pool.apply_async(self.crawl_page, (url,))
