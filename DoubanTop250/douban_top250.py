#! usr/bin/env python3
# -*- coding: utf-8 -*-

# 这是抓取豆瓣电影top250的爬虫,把电影名称、排名以及评分存入excel中
# 这是类版本
import os
from bs4 import BeautifulSoup
import lxml
import requests
import xlsxwriter

class DoubanTop250(object):
    def __init__(self,url):
        self.url = url
        
    def download_page(self,url):
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'}
        data = requests.get(url,headers = headers)
        return data.text

    def parse_html(self,html):
        soup = BeautifulSoup(html,'lxml')
        movie_list_soup = soup.find('ol',attrs = {'class':'grid_view'})

        movie_name_list = []
        movie_star_list = []
        movie_ranking_list = []
        for movie_li in movie_list_soup.find_all('li'): # 电影信息在标签'li'之间
            # 查找影片名称
            detail = movie_li.find('div',attrs = {'class':'hd'})
            movie_name = detail.find('span',attrs = {'class':'title'}).get_text()
            movie_name_list.append(movie_name + '\n')

            # 查找影片评分
            star_location = movie_li.find('div',attrs = {'class':'star'})
            star_score = star_location.find('span',attrs = {'class':'rating_num','property':'v:average'}).get_text()
            #print(star_score)
            movie_star_list.append(star_score + '\n') 

            # 查找影片排名
            ranking_location = movie_li.find('div',class_ = 'pic')
            ranking = ranking_location.find('em').get_text()
            #print(ranking)
            movie_ranking_list.append(ranking + '\n')
        
        next_page = soup.find('span',attrs = {'class':'next'}).find('a')
        #print(next_page)
        if next_page:
            return movie_name_list, movie_star_list, movie_ranking_list, self.url + next_page['href']
        return movie_name_list, movie_star_list, movie_ranking_list, None

    def main(self,url):
        workbook = xlsxwriter.Workbook('doubantop250-class.xlsx')
        top_format = workbook.add_format({'align':'center','font_size':14,'bold':True})
        others_format = workbook.add_format({'align':'center','font_size':12})

        worksheet = workbook.add_worksheet('电影排名清单')
        worksheet.set_column('A:A',13) # 设置第一列列宽为13
        worksheet.set_column('B:B',25)
        worksheet.set_column('C:C',13)

        headings = ['排名','名称','得分']
        #a = ['fasd','fasf','frfr']
        worksheet.write_row('A1',headings,top_format) # 按照行来写入,格式为top_format
        #worksheet.write_column('D1:D3',a,top_format) # 按照行来写入,格式为top_format
        for i in range(25):
            if url:
                
                html = self.download_page(url)
                [names,stars,rankings,url] = self.parse_html(html)

                worksheet.write_column(i*25+1,0,rankings,others_format) # 按照列来写入,格式为others_format     
                worksheet.write_column(i*25+1,1,names,others_format) # 按照列来写入,格式为others_format     
                worksheet.write_column(i*25+1,2,stars,others_format) # 按照列来写入,格式为others_format     
        workbook.close() # 关闭EXCEL文档


os.chdir('F:\\SpiderData')
url = 'https://movie.douban.com/top250'

doubantop250 = DoubanTop250(url)
doubantop250.main(url)
