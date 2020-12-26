import unittest
import os
from collections import namedtuple
from yarl import URL
from crawler.spider import Spider, FileWorker
from crawler.robotstxt_parser import RobotsTxtParser
from pathlib import Path

fields = ("html", "expected_1", "expected_2")
TestData = namedtuple("TestData", fields, defaults=(None,) * len(fields))


class TestHTMLParsing(unittest.TestCase):
    def test_find_links(self):
        cases = [
            TestData(
                '<li><a href="/ninjutsu/" title="Ниндзюцу">'
                '<li><a href="https://jut.su/taijutsu/" title="Тайдзюцу">',
                {"https://jut.su/ninjutsu/", "https://jut.su/taijutsu/"},
                {"j"},
            ),
            TestData(
                '<li><a href="https://drive.jut.su/taijutsu/" tle">'
                '<li><a href="http://but.su/ninjutsu/" title="н">',
                {"https://drive.jut.su/taijutsu/"},
                {},
            ),
            TestData(
                '<li><a href="/ninjutsu/" title="Ниндзюцу">'
                '<li><a href="ninjutsu/" title="Ниндзюцу">',
                {
                    "https://jut.su/ninjutsu/",
                    "https://jut.su/search/ninjutsu/",
                },
                {},
            ),
            TestData(
                '<li><a href="http://jut.su/taijutsu/" title="Тайдзюцу">',
                set(),
                {},
            ),
            TestData(
                '<li><a href="https://jut.su/taijutsu/bog.txt"'
                '<li><a href="#taijutsu/" title="Тайдзюцу">',
                set(),
                {},
            ),
            TestData(
                '<li><a href="https://jut.su/taijutsu#bog" title="Тайдзюцу">'
                '<li><a href="https://jut.su/taijutsu#jora" title="Тюцу">',
                {"https://jut.su/taijutsu"},
                {},
            ),
        ]
        spider = Spider(
            "jut.su",
            {"https://jut.su/", "drive.jut.su"},
            URL("https://jut.su/"),
            "tests", 0, False, 1, ('.txt', '.pptx')
        )
        i = 0
        for test_case in cases:
            with self.subTest(i):
                actual = spider.find_links(
                    test_case.html, URL("https://jut.su/search/")
                )
                self.assertEqual(
                    actual,
                    test_case.expected_1,
                    f"ex {test_case.expected_1} actual: {actual}",
                )
            i += 1

    def test_domain_settings(self):
        spider1 = Spider(
            "fuck.biden",
            {"trump.fuck.biden"},
            URL("https://yandex.ru"),
            "tests", 2, False, 1, ()
        )
        spider2 = Spider(
            "fuck.biden",
            {"fuck.biden"},
            URL("https://yandex.ru"),
            "tests", 2, False, 1, ()
        )
        cases = [
            TestData(
                '<a href="https://trump.fuck.biden/gay-sex" title="Тадзюцу">'
                '<a href="https://biden.fuck.biden/fiizon/ozatami" tile="ы">',
                {"https://trump.fuck.biden/gay-sex"},
                {
                    "https://biden.fuck.biden/fiizon/ozatami",
                    "https://trump.fuck.biden/gay-sex",
                },
            ),
            TestData(
                '<li><a href="https://black.trump.fuck.biden/gay-sex" le=у">'
                '<li><a href="https://biden.fuck.b.biden/fiiksiki-7sezon/o"',
                {"https://black.trump.fuck.biden/gay-sex"},
                {"https://black.trump.fuck.biden/gay-sex"},
            ),
        ]
        i = 0
        for test_case in cases:
            with self.subTest(i):
                actual1 = spider1.find_links(
                    test_case.html, URL("https://trump.fuck.biden")
                )
                actual2 = spider2.find_links(
                    test_case.html, URL("https://trump.fuck.biden")
                )
                self.assertEqual(actual1, test_case.expected_1, "1")
                self.assertEqual(actual2, test_case.expected_2, "2")
            i += 0

    def test_adding_links(self):
        spider = Spider(
            "jut.su",
            {"https://jut.su/"},
            URL("https://jut.su/"),
            "tests", 0, False, 1, ()
        )
        add_link = set()
        for i in range(10):
            add_link.add("https://jut.su/" + str(i))
        spider.check_new_links(add_link)
        for i in range(10):
            if spider.queue.get() not in add_link:
                raise self.failureException
        add_link.add("https://jut.su/10")
        spider.check_new_links(add_link)
        if spider.queue.get() != "https://jut.su/10":
            raise self.failureException

    def test_saving_file(self):
        crawler = Spider("yandex.ru", {"yandex.ru"}, URL("https://yandex.ru"),
                         "tester", 2, False, 1, ())
        crawler.save_page(URL("https://yandex.ru"), 'hhhhhhhhhhhhhh')
        crawler.save_page(URL("https://yandex.ru/help"), 'jjjjjjjjjjj')
        self.assertTrue(Path.cwd()/'tests'/'tester'/'yandex.txt')
        self.assertTrue(Path.cwd()/'tests'/'tester'/'yandex.ru'/'help.txt')


class TestRobotsTXTParsing(unittest.TestCase):
    def test_logic(self):
        raw_data = [
            "User-agent: *\nDisallow: /search/\nAllow: /gook",
            "User-agent: gosha\nDisallow: /search/"
            "\n\nUser-agent: *\n\nAllow: /gook",
            "User-agent: gosha\nDisallow: /search/"
            "\\nAllow: /gook\nUser-agent: *",
            "User-agent: *\nDisallow: /search/\n#giiiiiii",
        ]

        raw_answers_dis = [[".+/search/.+"], [], [], [".+/search/.+"]]
        raw_answers_allow = [[".+/gook.+"], [".+/gook.+"], [], []]
        for i in range(len(raw_data)):
            with self.subTest(i):
                parser = RobotsTxtParser("https://pythonworld.ru/")
                parser.make_sets(raw_data[i])
                self.assertEqual(parser.disallow_links, raw_answers_dis[i])
                self.assertEqual(parser.allow_links, raw_answers_allow[i])
                self.assertEqual(
                    parser.cant_fetch("https://gop/gook/kog"), False
                )


class TestFileWorker(unittest.TestCase):
    def test_file_to_set(self):
        work_set = FileWorker.file_to_set(Path.cwd()/"tests/test.txt")
        expected = {str(i) for i in range(1, 11)}
        self.assertEqual(expected, work_set, "sets")

    def test_create_dir(self):
        FileWorker.create_project_dir("test_dir", {"kip", "kap"})
        self.assertTrue(os.path.exists("test_dir"))
        self.assertTrue(os.path.exists("test_dir/kip"))
        self.assertTrue(os.path.exists("test_dir/kap"))


if __name__ == "__main__":
    unittest.main()
