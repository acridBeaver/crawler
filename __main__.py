import argparse
from queue import Queue
from yarl import URL

from app import file_worker
from app.robotstxt_parser import RobotsTxtParser
from app.spider import Spider


def get_domain_name(url: URL) -> str:
    *_, domain, root_domain = url.host.split('.')
    return f'{domain}.{root_domain}'


def set_up_arguments(arg_parser):
    arg_parser.add_argument('url', type=str, help='Ссылка на ресурс')
    arg_parser.add_argument('-s', '--save', action='store_true', help='Сохранять страницы в отдельные файлы')
    arg_parser.add_argument('-d', '--deep', type=int, default=99999, help='Глубина поиска')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    set_up_arguments(parser)
    args = parser.parse_args()
    base_url = args.url
    url = URL(base_url)
    domain_name = get_domain_name(url)
    robots_parser = RobotsTxtParser(base_url)
    file_worker.create_project_dir('hop')
    spider = Spider(domain_name, base_url, robots_parser, args.deep, args.save)
    spider.start()
    file_worker.set_to_file('hop/crawled.txt', spider.crawled)
    print('task done')
