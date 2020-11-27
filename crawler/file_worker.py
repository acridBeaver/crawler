import os


def create_project_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def write_file(path, data):
    with open(path, 'w') as file:
        file.write(data)


def file_to_set(file_name):
    result = set()
    with open(file_name, 'rt') as text:
        for line in text:
            result.add(line.replace('\n', ''))
    return result


def set_to_file(file_name, urls_set):
    with open(file_name, 'w') as file:
        for url in urls_set:
            file.write(url + '\n')
