#! usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Description:改版程序采用了多进程+协程的方式对meizitu的全站图片进行抓取
'''
__author__ = 'jqbk'
__date__ = '2017-07-01'
__version__ = '0.3'

import os
import re
import random
import time
import requests
import asyncio
import aiohttp
import multiprocessing
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

    async def request_page(self, pic_url):
        """
        返回具体图片地址的二进制内容，用于下载
        """
        # proxy = self.config_proxy()
        headers = self.config_user_agent()
        '''
        for each_proxy in proxy: 
            try:
                data = requests.get(single_url, headers=headers, proxies=each_proxy)
                data.encoding = 'gb2312'
            except requests.exceptions.ProxyError:
                pass
            else:
                break
        '''
        async with aiohttp.ClientSession() as session:
            async with session.get(pic_url, headers=headers) as response:
                response.encoding = 'gb2312'
                return await response.read() # read()方法用于下载二进制内容

    def get_selector(self, page_url):
        """
        获取网页页面的XML文档的节点对象
        """
        # proxy = self.config_proxy()
        headers = self.config_user_agent()
        page = requests.get(page_url, headers=headers)
        page.encoding = 'gb2312'
        html = etree.HTML(page.text)
        return html

    def get_page(self):
        """
        获取妹子图“极品分类”中各分类的名称和地址
        """
        selector = self.get_selector(self.url)
        urls = selector.xpath('//div[@class="tags"]/span/a/@href')
        names = selector.xpath('//div[@class="tags"]/span/a/@title')
        return urls, names

    def get_specific_url(self):
        """
        获取各分类页面下各个子页面的地址
        """
        # 只提取urls，不需要names
        urls = self.get_page()[0]
        integrated_url = None
        for each_page_url in urls:
            selector = self.get_selector(each_page_url)
            # 获取各分类页面下的最大页数
            try:
                max_page = selector.xpath('//div[@id="wp_page_numbers"]/ul/li[last()]/a/@href')[0]
            except IndexError:
                break
            else:
                # 用正则表达式提取最大页数
                max_number = re.search(r'\d{1,2}(?=\.html)', max_page)
                for number in range(int(max_number.group(0))): # 第0个子组,即匹配的内容
                    # 匹配到的“最大页”内容不同，需要分类处理
                    if not '/' in max_page:
                        integrated_url = self.url + '/a/' + max_page.replace(max_number.group(0)+'.html', str(number+1)+'.html')
                        yield integrated_url
                    else:
                        integrated_url = self.url + max_page.replace(max_number.group(0)+'.html', str(number+1)+'.html')
                        yield integrated_url

# 字符串和列表对象不能应用于await语句中
    def get_pic_url(self):
        """
        获取子页面下图片组的地址
        """
        integrated_gen = self.get_specific_url()
        while True:
            try:
                integrated_url = next(integrated_gen)
                selector = self.get_selector(integrated_url)
                pic_url = []
                # time.sleep(0.5) 
                pic_url.extend(selector.xpath('//li[@class="wp-item"]/div/div/a/@href'))
                # print(pic_url)
                yield pic_url
            except StopIteration:
                break

    async def download_every_pic(self, every_single_pic):
        """
        获取每张图片的具体地址，并下载保存
        """
        if every_single_pic:
            selector = self.get_selector(every_single_pic)
            
            every_single_pic_url = selector.xpath('//div[@id="picture"]/p/img/@src')
            every_single_pic_name = selector.xpath('//div[@id="picture"]/p/img/@alt')

            path = '/home/jawell/python/SpiderData/'
            os.chdir(path)
            for i in range(len(every_single_pic_url)):
                with open(path + every_single_pic_name[i] + '('+str(i+1)+')' + '.jpg', 'wb') as f:
                    time.sleep(0.5 + random.random())
                    print('正在下载名为:"%s"的图片，请稍后...' % (every_single_pic_name[i] + '('+str(i+1)+')'))
                    results = await self.request_page(every_single_pic_url[i])
                    f.write(results)
                    print('名为:"%s"的图片下载完成，准备下载下一张...\n' % (every_single_pic_name[i] + '('+str(i+1)+')'))

            print('======该部分下载完成!======\n')


if __name__ == '__main__':
    base_url = 'http://www.meizitu.com'
    DM = DownloadMeizitu(base_url)

    print('Parent process %s.' % os.getpid())

    pic_gen = DM.get_pic_url()
    start = time.time()
    while True:
        try:
            pic_url = next(pic_gen)
            loop = asyncio.get_event_loop()
            for every_single_pic in pic_url:
                loop.run_until_complete(DM.download_every_pic(every_single_pic))
            loop.close()
        except StopIteration:
            break

    stop = time.time()
    print('所有图片下载完成!')
    # 计算程序用时
    print('下载图片共用时:%.2f秒' % (stop-start))
