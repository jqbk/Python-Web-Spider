#! usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Description:这是用于定位妹子图片并自动下载的爬虫脚本
Date:Apr.2,2017
Author:Jawell Qi
notice:这个程序仍然很不完善，该网站目录很深，目前只抓取了‘巨乳’目录下第一页的内容
该脚本本打算使用多种浏览器模拟登陆以及随机代理，但是由于外国代理无法访问meizitu，故而没有使用随机代理
'''

from lxml import etree
import requests
import random
import re
import os

os.chdir('F:\\SpiderData\\妹子图')
user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]
UA = random.choice(user_agent_list)

ip_html = requests.get('http://haoip.cc/tiqu.htm')
iplist = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,4}', ip_html.text)

url = 'http://www.meizitu.com'
headers = {'User-Agent': UA}
start_html = requests.get(url, headers=headers)
start_html.encoding = 'gb2312'  # 改为gb2312编码，否则中文显示乱码
# print(start_html.text)
selector1 = etree.HTML(start_html.text)
page_url = selector1.xpath('//div[@class="topmodel"]/ul/li/a[@title="巨乳"]/@href')

for each_url in page_url:
    second_html = requests.get(each_url, headers=headers)
    second_html.encoding = 'gb2312'
    selector2 = etree.HTML(second_html.text)
    juru_url = selector2.xpath('//li[@class = "wp-item"]/div/div/a/@href')  # 注意，切不可写为:'//li[@class = "wp-item"]/*/a/@href'

img_url = []
for every_url in juru_url:
    UA = random.choice(user_agent_list)
    headers = {'User-Agent': UA}
    IP = random.choice(iplist)
    proxy = {'http': IP}  # 构造代理
    third_html = requests.get(every_url, headers=headers)  # 一开始打算使用随机代理,即 proxies = proxy，但是国外代理无法访问meizitu
    selector3 = etree.HTML(third_html.text)
    img_url += selector3.xpath('//div[@id ="picture"]/p/img/@src')

for every_image_url in img_url:
    img_html = requests.get(every_image_url, headers=headers)
    name = every_image_url[-12:-4].replace('/','-')
    with open('F:\\SpiderData\\妹子图\\' + name + '.jpg', 'wb') as f:
        f.write(img_html.content)
