#! usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Qi'
__date__ = '2017-05-02'

import os
import re
import requests
import random
import time
from lxml import etree
from util_config import CONFIG_USERAGENT_PC

class DownloadMeizitu(object):
    """
    下载“妹子图”网址下极品分类中的所有图片
    """
    def __init__(self, url=None):
        self.url = url

    def config_user_agent(self):
        """
        为每一次请求构造浏览器响应头
        """
        user_agent_list = CONFIG_USERAGENT_PC
        UA = random.choice(user_agent_list)
        return {'User-Agent': UA}

    def config_proxy(self):
        """
        为每一次请求构造代理IP
        """
        ip_url = 'http://www.data5u.com/free/'
        headers = self.config_user_agent()
        selector = etree.HTML(requests.get(ip_url, headers=headers).text)
        ip_list = selector.xpath('//ul[@class="l2"]/span[1]/li/text()')
        port_list = selector.xpath('//ul[@class="l2"]/span[2]/li/text()')
        port_type_list = selector.xpath('//ul[@class="l2"]/span[4]/li/a/text()')
        # 有的端口类型在网页上显示的是http,https，这类端口类型需要处理
        port_type_accurate = [each[:4] if len(each)>5 else each for each in port_type_list]
        result = [port_type + '#' + 'http://' + ip + ':' + port for port_type in port_type_accurate for ip in ip_list for port in port_list]
        # 去除重复元素
        result = list(set(result))
        # 剔除https代理(妹子图只支持http代理)
        result_sat = [each for each in result if each[:5] != 'https']
        return [{each.split('#', 1)[0].strip(): each.split('#', 1)[1].strip()} for each in result_sat]

    def request_page(self, single_url):
        """
        返回具体图片地址的二进制内容，用于下载
        """
        proxy = self.config_proxy()
        headers = self.config_user_agent() 
        data = requests.get(single_url, headers=headers, proxies=proxy)
        data.encoding = 'gb2312'
        return data.content

    def get_selector(self, page_url):
        """
        获取网页页面的XML文档的节点对象
        """
        proxy = self.config_proxy()
        headers = self.config_user_agent() 
        data = requests.get(page_url, headers=headers, proxies=proxy)
        data.encoding = 'gb2312' 
        selector = etree.HTML(data.text)
        return selector

    def get_page(self):
        """
        获取妹子图“极品分类”中各分类的名称和地址
        """
        selector = self.get_selector(self.url)
        urls = selector.xpath('//div[@class="topmodel"]/ul/li/a/@href')
        names = selector.xpath('//div[@class="topmodel"]/ul/li/a/@title')
        return urls, names

    def get_specific_url(self):
        """
        获取各分类页面下各个子页面的地址
        """
        # 只提取urls，不需要names
        urls = self.get_page()[0]
        integrated_url = []
        for each_page_url in urls:
            selector = self.get_selector(each_page_url)
            # 获取各分类页面下的最大页数
            try:
                max_page = selector.xpath('//div[@id="wp_page_numbers"]/ul/li[last()]/a/@href')[0]
            except IndexError:
                break
            else:
                # print(each_page_url)
                # print(max_page)
                # 用正则表达式提取最大页数
                max_number = re.search(r'\d{1,2}(?=\.html)', max_page)
                for number in range(int(max_number[0])): # 第0个子组,即匹配的内容
                    integrated_url.append(self.url + max_page.replace(max_number[0], str(number+1)))
                # print(max_number)
        return integrated_url

    def get_pic_url(self):
        """
        获取子页面下图片组的地址
        """
        for each_integrated_url in self.get_specific_url():
            pic_url = []
            selector = self.get_selector(each_integrated_url)
            # 设置延时访问
            time.sleep(0.5 + random.random())
            pic_url.extend(selector.xpath('//li[@class="wp-item"]/div/div/a/@href'))
            # print(pic_url)
            yield pic_url

    def download_every_pic(self):
        """
        获取每张图片的具体地址，并下载保存
        """
        gen = self.get_pic_url()
        while True:
            try:
                result = next(gen)
                for every_single_pic in result:
                    if every_single_pic:
                        time.sleep(0.5 + random.random())
                        selector = self.get_selector(every_single_pic)
                        
                        every_single_pic_url = selector.xpath('//div[@id="picture"]/p/img/@src')
                        every_single_pic_name = selector.xpath('//div[@id="picture"]/p/img/@alt')

                        path = 'F:\\SpiderData\\妹子图\\'
                        os.chdir(path)
                        for i in range(len(every_single_pic_url)):
                            with open(path + every_single_pic_name[i] + '('+str(i+1)+')' + '.jpg', 'wb') as f:
                                time.sleep(0.5 + random.random())
                                print('正在下载名为:"%s"的图片，请稍后...' % (every_single_pic_name[i] + '('+str(i+1)+')'))
                                f.write(self.request_page(every_single_pic_url[i]))
                                print('名为:"%s"的图片下载完成，准备下载下一张...\n' % (every_single_pic_name[i] + '('+str(i+1)+')'))

                print('======该部分下载完成!======\n')

            except StopIteration:
                break

        print('所有图片下载完成!')

start = time.time()

if __name__ == '__main__':
    base_url = 'http://www.meizitu.com'
    DM = DownloadMeizitu(base_url)
    # urls, names = get_page(url)
    # print(urls, names)
    DM.download_every_pic()
    # print(DM.config_proxy())
    # print(len(DM.get_pic_url()))

stop = time.time()
# 计算程序用时
print('下载图片共用时:%.2f秒' % (stop-start))
