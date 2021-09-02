import os
import pandas as pd

dict_keys = ['rating', 'rank', 'cover_url', 'is_playable', 'id', 'types', 'regions', 'title', 'url', 'release_date',
        'actor_count', 'vote_count', 'score', 'actors', 'is_watched']

def readAllFiles(filePath):
    fileList = os.listdir(filePath)
    data=pd.DataFrame(columns=['id','title'])
    for file in fileList:
        path = os.path.join(filePath, file)
        if os.path.isfile(path):
            df=pd.read_csv(path, encoding="utf-8-sig", header=0)
            data=pd.concat([data,pd.DataFrame(df.iloc[:,[4,7]])])
    return data
    
#这里的路径是你当前目录下的路径，看下图解释
if os.path.dirname(__file__):
    prefix=os.path.dirname(__file__)+"\\"
else:
    prefix=""
movies = readAllFiles(prefix+"Categories\\Data")
movies=movies.drop_duplicates()
movies.sort_values('id',inplace=True)
movies.to_csv(prefix+'index.csv', encoding="utf-8-sig", mode="w", index=False)