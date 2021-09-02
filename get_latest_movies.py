'''
Zhao ShiHao  2020-11-23
'''

import requests
import time
import json
import csv
import logging
import pandas as pd
import os
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.WARNING,#控制台打印的日志级别
                    filename='movie.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s [line: %(lineno)d] - %(levelname)s: %(message)s'
                    #日志格式
                    )

def get_latest_movies():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        }
    page = requests.get("https://movie.douban.com/coming", headers=headers).text
    soup=BeautifulSoup(page,'html.parser')
    list=soup.select_one(".coming_list").find_all("tr")
    quality_data=[]
    other_data=[]
    for i in range(1,5):
        tr=list[i]
        html=str(tr.a.get('href')) # 获取电影链接
        id=html[html.rfind("subject/")+len("subject/")+1:].replace("/", "")
        release_date_zh=tr.find("td").text.strip() #获取电影在中国大陆的上映时间
        movie=get_latest_movie_info(html,release_date_zh)
        if 'undefined' not in movie[-1]:
            quality_data.append(movie)
    return quality_data

def get_latest_movie_info(html,release_date_zh):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'accept':'application/json',
        }
    page = requests.get(html, headers=headers).text
    soup=BeautifulSoup(page,'html5lib')
    
    dict_keys=['name','image','director','author','actor','datePublished','genre','duration','aggregateRating']
    json_data= json.loads(soup.find('script', {'type': 'application/ld+json'}).get_text(),strict=False)

    flag=[]
    if '日' not in release_date_zh:
        flag.append('undefined')
    else:
        if '年' not in release_date_zh:
            release_date_zh="2020年"+release_date_zh
        release_date= time.strptime(release_date_zh,"%Y年%m月%d日")
        rs=soup.find_all('span', attrs={ 'property': 'v:initialReleaseDate'})
        if len(rs)>1:
            for r in rs:
                str=r.text
                try:
                    initial_release_date=time.strptime(str[:str.find("(")],"%Y-%m-%d")
                    if initial_release_date < release_date:
                        flag.append('late_released')
                except Exception as e:
                    print(str)
                    continue

    data=[html,(json_data[key] for key in dict_keys), release_date_zh, ','.join(flag)]
    return data

quality_data=get_latest_movies()
df=pd.DataFrame(quality_data,columns=['url','info','release_date','release_status'])
df.sort_values(by=['release_status','release_date'],ascending=[True,True],inplace=True, index=False)
print(df)