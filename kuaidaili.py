import time
import random
import re
from selenium import webdriver

import utils

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
# client = webdriver.Chrome(executable_path='/root/pythonwork/chromedriver/chromedriver', chrome_options=chrome_options)
client = webdriver.Chrome(chrome_options=chrome_options)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
}
str_list = []
server = utils.get_redis_client()


def dispose_url(get_url):
    # start_page = int(input('起始页码：'))
    # end_page = int(input('结束页码：'))
    ran = random.randint(1, 40)
    start_page = ran
    end_page = ran
    # 生成url
    for page in range(start_page, end_page + 1):
        # print(page)
        url = get_url + str(page) + '/'
        request(url)


def request(url):
    client.get(url)
    time.sleep(2)
    content_str = client.page_source
    str_list.append(content_str)


def content_str(string):
    IP = re.findall('<td data-title="IP">(\d.*?)</td>', str(string))
    PORT = re.findall('<td data-title="PORT">(\d.*?)</td>', str(string))
    for x, y in zip(IP, PORT):
        IP_PORT = x + ':' + y + '\n'
        utils.save_to_redis(str(IP_PORT))


def main():
    # print("kuaidaili working")
    get_url = 'https://www.kuaidaili.com/free/inha/'
    dispose = dispose_url(get_url)
    for string in str_list:
        content_str(string)
    client.quit()


if __name__ == '__main__':
    main()
