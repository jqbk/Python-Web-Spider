#! usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'jqbk'
__date__ = '2017-05-07'

import random
import requests
from lxml import etree
from util_config import CONFIG_USERAGENT_PC

class TestProxy(object):
    """
    检测爬取的IP地址是否可用
    """
    def __init__(self, url=None, test_url=None):
        self.url = url
        self.test_url = test_url

    def get_proxy(self):
        """
        获取代理网站的代理IP
        """
        headers = {'User-Agent': random.choice(CONFIG_USERAGENT_PC)}
        data = requests.get(self.url, headers=headers)
        data.encoding = 'utf-8'
        selector = etree.HTML(data.text)
        ip_list = selector.xpath('//tr/td[2]/text()')
        port_list = selector.xpath('//tr/td[3]/text()')
        return ip_list

if __name__ == '__main__':
    url = 'http://www.xicidaili.com/wt/'
    test_url = 'https://www.baidu.com'

    TP = TestProxy(url, test_url)
    print(TP.get_proxy())