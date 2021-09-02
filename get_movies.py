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

logging.basicConfig(level=logging.WARNING,#控制台打印的日志级别
                    filename='movie.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s [line: %(lineno)d] - %(levelname)s: %(message)s'
                    #日志格式
                    )

list = {"剧情": 11, "喜剧": 24, "动作": 5, "爱情": 13, "科幻": 17, "动画": 25, "悬疑": 11, "惊悚": 19, "恐怖": 20, "纪录片": 1, "短片": 23,
        "情色": 6, "同性": 26, "音乐": 14, "歌舞": 7, "家庭": 28, "儿童": 8, "传记": 2, "历史": 4, "战争": 22, "犯罪": 3, "西部": 27, "奇幻": 16,
        "冒险": 15, "灾难": 12, "武侠": 29, "古装": 30, "运动": 18, "黑色电影": 31,
        }
movie_type = "1"
name = "NONE"

def get_movie_html(start, limit):

    url = "https://movie.douban.com/j/chart/top_list?type="+str(movie_type)+"&interval_id=100%3A90&action=&start={}&limit={}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    }
    html = requests.get(url.format(start, limit), headers=headers).text
    time.sleep(10)
    #尽量设置一下睡眠吧，为了自己也为了别人
    return html

def init():
    global name
    for i in list:
        if str(movie_type) == str(list[i]):
            name = str(i)
            break
    dict_keys = ['rating', 'rank', 'cover_url', 'is_playable', 'id', 'types', 'regions', 'title', 'url', 'release_date',
            'actor_count', 'vote_count', 'score', 'actors', 'is_watched']
    df=pd.DataFrame(columns=dict_keys)
    df.to_csv(prefix+'Categories\\Data\\'+name+'_movie_info.csv', encoding="utf-8-sig", mode="w", index=False)

def work():
    start = 0
    limit = 50
    try:
        while True:
            data = []
            print("开始爬取"+name+"片排名为第"+str(start+1)+"到"+str(start+limit)+"的电影信息")
            try:
                data = get_movie_html(start, limit)
            except Exception as e:
                logging.warning(str(Exception)+'\n'+str(e))
            if len(data) == 2:
                break
            data = json.loads(data)    
            dict_keys = ['rating', 'rank', 'cover_url', 'is_playable', 'id', 'types', 'regions', 'title', 'url', 'release_date',
                 'actor_count', 'vote_count', 'score', 'actors', 'is_watched']
            json_data=[[i[key] for key in dict_keys] for i in data]
            df=pd.DataFrame(json_data)
            df.to_csv(prefix+'Categories\\Data\\'+name+'_movie_info.csv', encoding="utf-8-sig", mode="a", header=False, index=False)
            start += limit
        print(movie_type+"爬取完成！")
    except Exception as e:
        logging.error(str(Exception)+'\n'+str(e))
        print(str(Exception))
        print(str(e))
        print(movie_type+"爬取中断！")

def main():
    global movie_type
    global prefix
    if os.path.dirname(__file__):
        prefix=os.path.dirname(__file__)+"\\"
    else: prefix=""

    for i in list.values():
        movie_type = str(i)
        init()
        try:
            work()
        except Exception as e:
            logging.exception(e)
	#可以选择根据需要爬取
    # print("选择需要爬取的类型的数字(输入“all”全部爬取)")
    # for i in list:
    #     print(i+":"+str(list[i]))
    # type = input()
    # if type == "all":
    #     for i in list.values():
    #         movie_type = str(i)
    #         init()
    #         work()
    # else:
    #     movie_type = type
    #     init()
    #     work()

if __name__=="__main__":
    main()
