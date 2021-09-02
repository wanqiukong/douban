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
index_name=prefix+"index.txt"
comment_name=prefix+"comment.txt"

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
    cookie=r'll="108231"; bid=e5PT--d675Y; __utmv=30149280.331; __yadk_uid=EvsGYr8wx8ReXNvmNynWscQEl9bLyXvl; push_doumail_num=0; gr_user_id=542a7f2d-db27-4a7c-a8cd-5b9b30815a48; douban-fav-remind=1; push_noty_num=0; ct=y; __gads=ID=d839a4bf5cdd8ccb-22bdcab044c90027:T=1623047097:RT=1623047097:S=ALNI_MZPHYVhuSJHRoPITe3JkTxybWxoaA; __utmz=30149280.1623296910.16.9.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _pk_ses.100001.8cb4=*; _pk_ref.100001.8cb4=["","",1623907998,"https://accounts.douban.com/passport/login?redir=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F1291828%2F"]; ap_v=0,6.0; __utma=30149280.90829439.1617950106.1623377035.1623908018.19; __utmc=30149280; __utmt=1; _pk_id.100001.8cb4=09d3ae2122fd3b7a.1617943937.15.1623908154.1623377030.; __utmb=30149280.4.10.1623908018; dbcl2="3310037:l6nZa9pgf4k"'
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
    print(base_url.format(movie_id, start, sort, rank))
    html = requests.get(base_url.format(movie_id, start, sort, rank), headers=headers).text
    time.sleep(7)
    return html

def get_comment_quantity(id):
    html = get_comment_html(id, '1','new_score','h')
    soup = BeautifulSoup(html, 'html.parser')
    li=soup.find('li',class_="is-active")
    str=li.text

    quantity_left = quantity_right = 0
    for i in range(len(str)):
        if str[i] == '(':
            quantity_left = i + 1
        elif str[i] == ')':
            quantity_right = i
    quantity = int(str[quantity_left:quantity_right])

    return quantity
    

def hot_comments(movie_name, movie_id):
    # 获取短评总数量
    comment_quantity = get_comment_quantity(movie_id)
    print("电影《"+movie_name + "》共有" + str(comment_quantity) + "条短评")

    #开始爬取热门短评
    ranks=['h','m','l']
    cols=['user','rank','votes','description','date']
    limit=20
    if (os.path.exists(comment_name) and os.path.isfile(comment_name)):
        with open(comment_name, 'r', encoding='utf-8-sig') as f:
            lines = f.read().split('\n')
            rank=lines[0]
            past_comment=int(lines[1])
    else:
        with open(comment_name, 'w', encoding='utf-8-sig') as f:
            f.write('h\r0')
        rank= "h"
        past_comment=0
            
    comment_counter=0
    for i in range(ranks.index(rank),len(ranks)):
        start=0
        while True:
            try:
                movie_comments_raw = get_comment_html(movie_id, start, 'new_score', ranks[i])
                movie_comments, n =comment_preprocess(movie_comments_raw)
                if n==0:
                    break
                df=pd.DataFrame(movie_comments, columns=cols)
                name=prefix+"Data/Comments/"+movie_name+"_"+str(movie_id)+"_comments_"+scrapy_time+"_"+str(comment_quantity)+pc+".csv"
                if i==0 and start==0:
                    df.to_csv(name, encoding="utf-8-sig", mode="w", index=False)
                    print(name)
                else:
                    df.to_csv(name, encoding="utf-8-sig", mode="a", header=False, index=False)
            except Exception as e:
                logging.warning(str(Exception)+'\n'+str(e))
                print(str(Exception))
                print(str(e))
                print(" -爬取电影《"+movie_name+ "第" + str(comment_counter+start+n+1)+"条热门短评失败！")
                with open(comment_name, 'w', encoding='utf-8-sig') as f:
                    f.write(ranks[i]+'\r'+str(start+n))
                break
            start+=limit
        comment_counter+=start    

    # 将页数归零
    with open(comment_name, 'w', encoding='utf-8-sig') as f:
        f.write('h\r0')
    
def comment_preprocess(comments_raw):
    soup=BeautifulSoup(comments_raw,'html.parser')
    percent=soup.select_one('.comment-filter').select('.comment-percent')
    global pc
    pc=''
    pc=pc.join( [","+percent[i].text for i in range(1,len(percent))])

    # 每组class 均为comment-item  这样分成20条记录(每个url有20个评论)
    node = soup.select('.comment-item') 
    comments=[]
    comments_number=0
    try:
        for va in node: # 遍历评论
            user=str(va.a.get('href')) # 获取评论者名称
            user=user[user.index("people/")+len("people/")+1:-1]
            star = va.select_one('.comment-info').select('span')[1].get('class')[0][-2] # 星数好评
            votes = va.select_one('.votes').text # 投票数
            comment = va.select_one('.short').text # 评论文本
            date=va.select_one('.comment-time').get('title') #评论时间
            comments.append([user, star, votes, comment,date])   
            comments_number+=1
    except Exception as e: # 有异常退出
        print(e)
    return comments,comments_number

def main():
    if (os.path.exists(index_name) and os.path.isfile(index_name)):
        with open(index_name, 'r') as f:
            index = f.read()
    else:
        with open(index_name, 'w') as f:
            f.write('0')
        index=0
    sleep_count = 1

    global movie_percents
    df=pd.read_csv(prefix+"index.csv", encoding="utf-8-sig", header=0)
    movie_id=df.iloc[:,0]
    movie_name=df.iloc[:,1]

    global scrapy_time
    try:
        if len(movie_name) == 0 and len(movie_id) == 0:
             print("爬取结束！\n退出爬取！")
        else:
            for i in range(int(index), len(movie_name)):
                if sleep_count % 5 == 0:
                    time.sleep(random.randint(600, 900))
                sleep_count += 1

                try:      
                    scrapy_time=time.strftime("%Y%m%d%H%M%S", time.localtime())
                    hot_comments(movie_name[i], movie_id[i])  
                    print("成功爬取电影《"+movie_name[i] + "》的所有热门短评！")
                    with open(index_name, 'w') as f:
                        f.write(str(i + 1))
                except Exception as e:
                    logging.error(str(Exception) + '\n' + str(e))
                    print("保存电影《" + movie_name[i] + "》失败！睡眠开始！")
                    time.sleep(random.randint(100, 200))
                    with open(index_name, 'w') as f:
                        f.write(str(i+1))
                    main()
                index = i
    except Exception as e:
        with open(index_name, 'w') as f:
             f.write(str(index))
        logging.error(str(Exception) + '\n' + str(e))
        print("爬取【序号" + str(index+1) + "】电影《"+movie_name[i] + "》失败，退出爬取！")
        return

if __name__ == '__main__':
    main()
