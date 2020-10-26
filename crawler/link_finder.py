import yarl
from yarl import URL
import requests
from bs4 import BeautifulSoup


HEADERS = {
	'User-Agent': 'Mozilla/5.0',
	'Connection': 'keep - alive',
}


class LinkFinder:

	def __init__(self, domain_name: str, url: URL):
		self.url = url
		self.domain_name = domain_name
		self.host_name = self.get_host_name()
		self.link = str(url)
		self.links = set()

	def get_host_name(self):
		return self.url.scheme + '://' + self.url.host

	def find_links(self, html: str):
		soup = BeautifulSoup(html, 'html.parser')
		for obj in soup.find_all('a', href=True):
			link = obj['href']
			if link.endswith(('.jpg', '.pptx')):
				continue
			link = URL(link)
			if self.domain_name in link and link.startswith(self.url.scheme):
				self.links.add(link)
			elif link.scheme is not ('https://', 'http://'):
				if not link.startswith('/'):
					parent_link = yarl.URL()
					new_link = parent_link.parent / link
				self.links.add(self.host_name + link)

	def get_links(self):
		site_info = self.get_content(self.link)
		if site_info is None or site_info.status_code != 200:
			return
		html = site_info.text
		self.find_links(html)

	@staticmethod
	def get_content(link):
		try:
			result = requests.get(link)
		except ConnectionError:
			return None
		return result
