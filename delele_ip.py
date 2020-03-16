import utils
import settings
import time
import requests
import threading
from gevent.pool import Pool


class ExpireIpCleaner:

    def __init__(self):
        self.logger = utils.get_logger(getattr(self.__class__, '__name__'))
        self.server = utils.get_redis_client()

    def clean_by_time(self):
        """
        清理代理池中的过期ip
        :return:
        """
        self.logger.info('开始清理过期ip')
        # 计算清理前代理池的大小
        total_before = int(self.server.zcard(settings.IP_POOL_KEY))
        # 清理
        self.server.zremrangebyscore(settings.IP_POOL_KEY, 0, int(time.time()))
        # 计算清理后代理池的大小
        total_after = int(self.server.zcard(settings.IP_POOL_KEY))
        self.logger.info('过期ip清理前可用ip {}，清理后可用ip {}'.format(total_before, total_after))

    def main(self):
        """
        周期性的清理过期ip
        :return:
        """
        while True:
            self.clean_by_time()
            self.logger.info('*' * 40)
            time.sleep(settings.CLEAN_INTERVAL)


class CleanCheck:

    def __init__(self):
        self.logger = utils.get_logger(getattr(self.__class__, '__name__'))
        self.server = utils.get_redis_client()
        self.bad_proxy_list = []
        self.pool = Pool(50)

    def check(self, proxy):
        """
        检查代理是否可用，
        并将可用代理加入到指定列表中
        :param proxy:
        :return:
        """
        if settings.USE_PASSWORD:
            tmp_proxy = '{}:{}@{}'.format(settings.USERNAME, settings.PASSWORD, proxy)
        else:
            tmp_proxy = '{}'.format(proxy)
        proxies = {
            'http': 'http://' + tmp_proxy,
            'https': 'https://' + tmp_proxy,
        }
        try:
            # 验证代理是否可用时，访问的是ip138的服务  http://2019.ip138.com/ic.asp
            resp = requests.get('http://www.baidu.com', proxies=proxies, timeout=10)
            # self.logger.info(resp.content.decode('gb2312'))
            # 判断是否成功使用代理ip进行访问
            assert resp.status_code == 200
            self.logger.info('[GOOD] - {}'.format(proxy))
        except Exception as e:
            self.logger.info('[BAD] - {} , {}'.format(proxy, e.args))
            self.bad_proxy_list.append(proxy)

    def clean_by_check(self):
        """
        清理代理池中的过期ip
        :return:
        """
        self.logger.info('开始清理不可用ip')
        # 计算清理前代理池的大小
        total_before = int(self.server.zcard(settings.IP_POOL_KEY))
        # 清理
        proxy_ips = self.server.zrangebyscore(settings.IP_POOL_KEY, int(time.time()),
                                              int(time.time()) + settings.PROXY_IP_TTL * 10)
        # print('proxy_ips-->',proxy_ips)
        self.bad_proxy_list.clear()
        for i, proxy in enumerate(proxy_ips):
            proxy_ips[i] = proxy.decode()
        self.pool.map(self.check, proxy_ips)
        self.pool.join()
        for badproxy in self.bad_proxy_list:
            self.server.zrem(settings.IP_POOL_KEY, badproxy)
        # 计算清理后代理池的大小
        total_after = int(self.server.zcard(settings.IP_POOL_KEY))
        self.logger.info('不可用ip清理前可用ip {}，清理后可用ip {}'.format(total_before, total_after))

    def main(self):
        """
        周期性的清理不可用ip
        :return:
        """
        while True:
            self.clean_by_check()
            time.sleep(settings.CLEAN_CHECK)


def begin():
    clean_by_check = threading.Thread(target=CleanCheck().main)
    clean_by_check.start()
    clean_by_time = threading.Thread(target=ExpireIpCleaner().main)
    clean_by_time.start()


if __name__ == '__main__':
    begin()
