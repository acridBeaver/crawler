import threading
from queue import Queue
from app import file_worker
from app.spider import Spider
from yarl import URL

NUMBER_OF_THREADS = 8


def get_domain_name(url: URL):
    input_host = str.split(url.host, '.')
    return input_host[-2] + '.' + input_host[-1]


def crawl(queue_file: str):
    queue_links = file_worker.file_to_set(queue_file)
    if len(queue_links) > 0:
        print('i am alive')
        create_jobs(queue_file)


def create_jobs(queue_file):
    for link in file_worker.file_to_set(queue_file):
        queue.put(link)
    queue.join()
    crawl(queue_file)


def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


def work():
    while True:
        url = queue.get()
        spider.crawl_page(url)
        queue.task_done()


def update_queue(queue):
    for link in file_worker.file_to_set(queue_file):
        queue.append(link)


if __name__ == '__main__':
    base_url = input('введите ссылку для кравлинга \n')
    base_url = base_url[0:-1]
    url = URL(base_url)
    name = 'dir'
    queue_file = name + '/queue.txt'
    domain_name = get_domain_name(url)
    file_worker.create_project_dir(name)
    file_worker.create_data_files(name, base_url)
    spider = Spider(name, domain_name, base_url)
    queue = []
    update_queue(queue)
    while len(queue) > 0:
        while len(queue) > 0:
            url = queue.pop()
            print('crawling ' + url)
            spider.crawl_page(url)
        update_queue(queue)
    print('task done')
