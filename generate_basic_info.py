from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pandas as pd
import os
import time


def parse_basic_info(file_list):
    data = []
    for file in file_list:
        name = os.path.join(file)
        name = name.replace('.csv','')
        name = name.strip().split('_')
        vote = name[-1].split(',')
        t = time.strptime(name[3], "%Y%m%d%H%M%S")
        row = [name[1], name[0], vote[0],vote[1:], time.strftime("%Y-%m-%d %H:%M:%S", t)]
        data.append(row)
    return data


def get_basic_info(path):
    # TODO 临时文件放到临时文件夹中 tmp/
    l = pd.read_csv(path + "/index.csv", encoding="utf-8-sig", header=0)
    file_list = os.listdir(path+'/Data/Comments')
    print("总计" + str(l.shape[0]) + "部电影，到目前已爬虫" + str(len(file_list)) + "部电影")
    
    data = parse_basic_info(file_list)
    df = pd.DataFrame(data, columns=['id', 'title', 'rating_count', 'rating_percent', 'access_date'])
    df.sort_values(by="id")
    df.to_csv(path + "/crawled_movies.csv", encoding="utf-8-sig", mode="w", index=False)
    print("— 已保存所有爬虫电影的索引信息")

# TODO 永远使用相对路径
get_basic_info("C:/users/wanqiu/OneDrive/douban")