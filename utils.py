from redis import StrictRedis, ConnectionPool
import settings
import logging
import time

def get_redis_client():
    """
    获取一个redis连接
    :return:
    """
    return StrictRedis(host=settings.REDIS_SERVER_HOST, port=settings.REDIS_SERVER_PORT, db=settings.REDIS_SERVER_DB,
                       password=settings.REDIS_SERVER_PWD)

def save_to_redis(proxy):
    """
    将提取到的有效ip保存到redis中，
    供其他组件访问
    :return:
    """
    if proxy:
        get_redis_client().zadd(settings.IP_POOL_KEY, {proxy: int(time.time()) + settings.PROXY_IP_TTL})
        get_logger('sve-to-redis').info(proxy)


def get_logger(name=__name__):
    """
    获取一个logger，用以格式化输出信息
    :param name:
    :return:
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    # 使用StreamHandler输出到屏幕
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
