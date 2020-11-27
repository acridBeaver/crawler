import requests


class RobotsTxtParser:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.allow_links = []
        self.disallow_links = []
        self.make_sets()

    def make_sets(self):
        try:
            doc = requests.get(self.base_url + 'robots.txt')
        except ConnectionError:
            print('site haven`t robots.txt')
            return
        if doc.status_code != 200:
            print('site haven`t robots.txt')
            return
        for fragment in doc.text.split('\n\n'):
            for line in fragment.split('\n'):
                if line.startswith('#'):
                    continue
                if line != 'User-agent: *' and not line.startswith(('Disallow:', 'Allow:')):
                    break
                params = line.rsplit(' ', maxsplit=1)
                if params[0] == 'Disallow:':
                    self.disallow_links.append(params[1].strip().replace('*', ''))
                if params[0] == 'Allow:':
                    self.allow_links.append(params[1].strip().replace('*', ''))

    def cant_fetch(self, link):
        for disallow in self.disallow_links:
            if disallow in link:
                for allow in self.allow_links:
                    if allow in link:
                        return False
                return True
