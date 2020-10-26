import pytest
from crawler.link_finder import LinkFinder

with open(file_name, 'w') as file:
    for url in urls_set:
        file.write(url + '\n')
