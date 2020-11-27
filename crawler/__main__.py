import argparse
from queue import Queue
from yarl import URL

from crawler import file_worker, errors
from crawler.robotstxt_parser import RobotsTxtParser
from crawler.spider import Spider


def get_domain_name(url: URL) -> str:
    *_, domain, root_domain = url.host.split('.')
    return f'{domain}.{root_domain}'


def set_up_arguments(arg_parser):
    arg_parser.add_argument('url', type=str, help='Ссылка на ресурс')
    arg_parser.add_argument('-f','--dir', type=str, default='hop', help='рабочая директория')
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
    file_worker.create_project_dir(args.dir)
    try
        spider = Spider(domain_name, base_url, robots_parser,args.dir, args.deep, args.save)
        spider.start()
        file_worker.set_to_file(args.dir + '/crawled.txt', spider.crawled)
    except errors.CrawlerError as e:
        log.error(e.message)
    except KeyboardInterrupt:

        exit(1)
    print('task done')
