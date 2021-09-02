import logging
import re
import time
import random
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup


if os.path.dirname(__file__):
    prefix=os.path.dirname(__file__)+"/"
else:
    prefix=""    

logging.basicConfig(level=logging.WARNING,  # 控制台打印的日志级别
                    filename=prefix+'movie_comment.log',
                    filemode='w',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    # 日志格式
                    )

def get_user_agent():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)',
        '(Windows NT 10.0; WOW64)',
        '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    user_agent = ''.join(['Mozilla/5.0',
                          random.choice(os_type),
                          'AppleWebKit/537.36',
                          '(KHTML, like Gecko)',
                          chrome_version,
                          'Safari/537.36'
                          ])
    return user_agent

def get_comment_html(movie_id, start, sort, rank):
    cookie=r'll="118371"; bid=OR_ri6ItpYc; __utmv=30149280.331; __yadk_uid=Tos4nxUPA3RJM69mnN5qmv0NZXlJKqnK; douban-fav-remind=1; douban-profile-remind=1; _vwo_uuid_v2=D484B29D396A2218A66ECDCCB1155BC0F|540ad863d03c0d21d0224a225089a18a; __gads=ID=8981b29009d8466b:T=1613288710:S=ALNI_MY0r3ZCtaMWd561iGLUYPwt54rfVA; gr_user_id=46f99f1d-ebf4-4e38-9a9e-39f5ad082e52; push_doumail_num=0; __utmz=30149280.1619527675.35.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); push_noty_num=0; ct=y; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1623080948%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.849814829.1609414876.1622721292.1623080949.42; __utmc=30149280; __utmt=1; ap_v=0,6.0; _pk_id.100001.8cb4=3bd33d64540e3a2e.1609414875.42.1623081038.1622721290.; __utmb=30149280.6.10.1623080949; dbcl2="3310037:GB7piuCaHXQ"; ck=AiVj'
    headers = {
        'User-Agent': get_user_agent(),
        'Connection':'keep-alive',
        'accept':'application/json',
        'Cookie':cookie
    }

    #status：P, 看过; F，想看
    #sort：new_score，热门排序(每种评价最多500条)；time，时间排序(最多300条)
    #percent_type: h, 好评；m，中评；l，差评
    base_url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20&status=P&sort={}&percent_type={}' 
    html = requests.get(base_url.format(movie_id, start, sort, rank), headers=headers).text
    time.sleep(7)
    return html