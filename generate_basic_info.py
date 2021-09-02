from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pandas as pd
import os
import time
    
def parse_basic_info(fileList):
    data=[]
    for file in fileList:
        name = os.path.join(file)
        name=name.replace('.csv','')
        name=name.strip().split('_')
        vote=name[-1].split(',')
        t = time.strptime(name[3],"%Y%m%d%H%M%S")
        row=[name[1], name[0], vote[0],vote[1:], time.strftime("%Y-%m-%d %H:%M:%S", t)]
        data.append(row)
    return data
    
def get_basic_info(path):
    l=pd.read_csv(path+"/index.csv", encoding="utf-8-sig", header=0)
    fileList = os.listdir(path+'/Data/Comments')
    print("总计"+str(l.shape[0])+"部电影，到目前已爬虫"+str(len(fileList))+"部电影")
    
    data=parse_basic_info(fileList)
    df=pd.DataFrame(data,columns=['id','title','rating_count','rating_percent','access_date'])
    df.sort_values(by="id")
    df.to_csv(path+"/crawled_movies.csv", encoding="utf-8-sig", mode="w",index=False)
    print("— 已保存所有爬虫电影的索引信息")
     
get_basic_info("C:/users/wanqiu/OneDrive/douban")