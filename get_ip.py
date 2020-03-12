# -*- coding: utf-8 -*-
# @File  : get_ip.py
# @Author: AaronJny
# @Date  : 18-12-14 上午10:44
# @Desc  : 从指定网站上获取代理ip,
#          我目前在使用站大爷，就以站大爷为例
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()
import requests
import time
import utils
import settings
import re
from  crawler import crawler

ip_pool_key = settings.IP_POOL_KEY
class ZdyIpGetter:
    """
    从`站大爷`上提取代理ip的脚本，使用其他代理服务的可自行编写相关脚本，
    原理和逻辑都是相通的，部分细节上需要针对处理
    """

    def __init__(self):
        # 购买服务时，网站给出的提取ip的api，替换成自己的
        self.api_url = 'http://www.89ip.cn/tqdl.html?api=1&num=60&port=&address=&isp='
        self.logger = utils.get_logger(getattr(self.__class__, '__name__'))
        self.proxy_list = []
        self.good_proxy_list = []
        self.pool = Pool(5)
        self.server = utils.get_redis_client()

    def get_proxy_list(self):
        crawler.run()


    def fetch_new_ip(self):
        """
        获取一次新ip的整体流程控制
        :return:
        """
        self.proxy_list.clear()
        self.good_proxy_list.clear()
        self.get_proxy_list()
        # self.save_to_redis()

    def main(self):
        """
        周期获取新ip
        :return:
        """
        start = time.time()
        while True:
            # 每 settings.FETCH_INTERVAL 秒获取一批新IP
            if time.time() - start >= settings.FETCH_INTERVAL:
                self.fetch_new_ip()
                start = time.time()
            time.sleep(2)


if __name__ == '__main__':
    ZdyIpGetter().main()
