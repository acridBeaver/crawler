import file_worker
from spider import Spider
from yarl import URL


def get_base_url(url: URL):
    input_host = str.split(url.host, '.')
    return input_host[-2] + '.' + input_host[-1]


link = input('введите ссылку для кравлинга \n')
link = link[0:-1]
url = URL(link)
name = 'hop'
base_url = get_base_url(url)
print(base_url)
host_name = url.scheme + '://' + url.host
print(host_name)
file_worker.create_project_dir(name)
file_worker.create_data_files(name, link)
ra = int(input('введите глубину \n'))
for _ in range(1, ra):
    spider = Spider(name, base_url, host_name)
