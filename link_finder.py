from yarl import URL
import requests
from bs4 import BeautifulSoup


HEADERS = {
	'User-Agent': 'Mozilla/5.0',
	'Connection': 'keep - alive',
}


class LinkFinder:

	def __init__(self, base_url: str, host_name: str, url: URL):
		self.url = url
		self.base_url = base_url
		self.host_name = host_name
		self.link = url.__str__()
		self.links = set()

	def find_links(self, html: str):
		soup = BeautifulSoup(html, 'html.parser')
		for obj in soup.find_all('a', href=True):
			link = obj['href']
			if link.endswith('.jpg') or link.endswith('.pptx'):
				continue
			if self.base_url in link and link.startswith(self.url.scheme):
				self.links.add(link)
			elif link[0:8] != 'https://' and link[0:7] != 'http://':
				if not link.startswith('/'):
					link = '/' + link
				self.links.add(self.host_name + link)

	def get_links(self):
		site_info = self.get_content(self.link)
		if site_info.status_code != 200 or site_info is None:
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




#c = get_content('https://ru.wikipedia.org#Ссылки')
#i = find_links(c.text, 'https://ru.wikipedia.org')
#url = URL('https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8')
#c = get_links('https://ru.wikipedia.org')

#print(url.name)

