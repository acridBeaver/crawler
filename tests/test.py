import unittest
from collections import namedtuple
from yarl import URL
from crawler.spider import Spider
from crawler.robotstxt_parser import RobotsTxtParser

TestData = namedtuple('TestData', ['html', 'expected'])


class TestHTMLParsing(unittest.TestCase):
    def test_find_links(self):
        cases = [TestData('<li><a href="/ninjutsu/" title="Ниндзюцу">'
                          '<li><a href="https://jut.su/taijutsu/" title="Тайдзюцу">',
                          {'https://jut.su/ninjutsu/', 'https://jut.su/taijutsu/'}),
                 TestData('<li><a href="https://drive.jut.su/taijutsu/" title="Тайдзюцу">'
                          '<li><a href="http://but.su/ninjutsu/" title="Ниндзюцу">',
                          {'https://drive.jut.su/taijutsu/'}),
                 TestData('<li><a href="/ninjutsu/" title="Ниндзюцу">'
                          '<li><a href="ninjutsu/" title="Ниндзюцу">',
                          {'https://jut.su/ninjutsu/', 'https://jut.su/search/ninjutsu/'}),
                 TestData('<li><a href="http://jut.su/taijutsu/" title="Тайдзюцу">', set()),
                 TestData('<li><a href="https://jut.su/taijutsu/bog.txt" title="Тайдзюцу">'
                          '<li><a href="#taijutsu/" title="Тайдзюцу">',
                          set()),
                 TestData('<li><a href="https://jut.su/taijutsu#bog" title="Тайдзюцу">'
                          '<li><a href="https://jut.su/taijutsu#jora" title="Тайдзюцу">',
                          {'https://jut.su/taijutsu'})]
        spider = Spider('jut.su', 'https://jut.su/', RobotsTxtParser('https://jut.su/'), 0, False)
        for test_case in cases:
            actual = spider.find_links(test_case.html, URL('https://jut.su/search/'))
            self.assertEqual(actual, test_case.expected)

    def test_adding_links(self):
        spider = Spider('jut.su', 'https://jut.su/', RobotsTxtParser('https://jut.su/'), 0, False)
        add_link = set()
        for i in range(10):
            add_link.add('https://jut.su/' + str(i))
        spider.check_new_links(add_link)
        for i in range(10):
            if spider.queue.get() not in add_link:
                raise self.failureException
        add_link.add('https://jut.su/10')
        spider.check_new_links(add_link)
        if spider.queue.get() != 'https://jut.su/10':
            raise self.failureException


if __name__ == '__main__':
    unittest.main()
