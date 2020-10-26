import os


def create_project_dir(project_name):
    if not os.path.exists(project_name):
        os.makedirs(project_name)


def create_data_files(site_name, base_url):
    queue = site_name + '/queue.txt'
    crawled = site_name + '/crawled.txt'
    if not os.path.isfile(queue):
        write_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')


def write_file(path, data):
    with open(path, 'w') as f:
        f.write(data)


def file_to_set(file_name):
    with open(file_name, 'r') as text:
        return set(line.rstrip() for line in text)


def set_to_file(file_name, urls_set):
    with open(file_name, 'w') as file:
        for url in urls_set:
            file.write(url + '\n')
