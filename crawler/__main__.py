import argparse
import logging
import datetime
from pathlib import Path

from yarl import URL

from crawler.spider import Spider, FileWorker


def set_up_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("url", type=str, help="Ссылка на ресурс")
    arg_parser.add_argument(
        "-f", "--dir", type=str, default="#", help="рабочая директория"
    )
    arg_parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Сохранять страницы в отдельные файлы",
    )
    arg_parser.add_argument(
        "-d", "--deep", type=int, default=99999, help="Глубина поиска"
    )
    arg_parser.add_argument(
        "-p", "--pool", type=int, default=5, help="Количество потоков"
    )
    arg_parser.add_argument('-e', '--disallow_ends', type=str, nargs='+',
                            default=(".jpg", ".png", ".pptx", ".txt", "xml"),
                            help='Редактироваие допустимых окончаний ссылки')
    domains = arg_parser.add_mutually_exclusive_group()
    domains.add_argument(
        "-D", "--cmd_domain", type=str, default=False, nargs='+',
        help="установить разрешенные домены." " Формат ввода: <domain>",
    )
    domains.add_argument(
        "-F",
        "--file_domains",
        action="store_true",
        help="установить разрешенные домен "
        "из файла Crawler/domain_setup.txt",
    )
    return arg_parser.parse_args()


def get_domains(link: URL) -> (str, set):
    *_, domain, root_domain = link.host.split(".")
    first_domain = f"{domain}.{root_domain}"
    domains_list = set()
    if args.cmd_domain:
        for string in args.cmd_domain:
            domains_list.add(string)
    if args.file_domains:
        domains_list = FileWorker.file_to_set("domain_setup.txt")
    if args.dir == "#":
        args.dir = str(datetime.datetime.now())
    if len(domains_list) == 0 or first_domain in domains_list:
        domains_list.clear()
        domains_list.add(first_domain)
    FileWorker.create_project_dir(args.dir, domains_list)
    return first_domain, domains_list


if __name__ == "__main__":
    logging.basicConfig(
        filename="app.log",
        filemode="w",
        format="%(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    args = set_up_arguments()
    url = URL(args.url)
    base_domain, allow_domains = get_domains(url)
    logging.info(
        f"{base_domain} and {allow_domains}," f"url = {url.human_repr()}"
    )
    spider = Spider(
        base_domain, allow_domains, url, args.dir, args.deep, args.save,
        args.pool, tuple(args.disallow_ends))
    try:
        spider.start()
    except KeyboardInterrupt:
        FileWorker.set_to_file(Path.cwd()/args.dir/"crawled.txt",
                               spider.crawled)
        exit(1)
    logging.info(len(spider.crawled))
    FileWorker.set_to_file(Path.cwd()/args.dir/"crawled.txt", spider.crawled)
    print("task done")
