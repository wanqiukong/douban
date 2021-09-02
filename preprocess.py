import os
from shutil import copyfile

def distinct(dir):
    files=os.listdir(dir)
    ids=[]
    times=[]
    fsize=[]
    for file in files:
        info=os.path.splitext(file)[0].split('_')
        ids.append(info[1])
        times.append(info[3])
        fsize.append(os.path.getsize(dir+"/"+file))
    distinct_ids=set(ids)
    for id in distinct_ids:
        index=get_index(ids,id)
        if len(index)>1:
            fset=[fsize[i] for i in index]
            largest=get_index(fset,max(fset))
            timeset=[times[index[l]] for l in largest]
            tindex=timeset.index(max(timeset))
            file=files[index[largest[tindex]]]
        else:
            file=files[index[0]]

        copyfile(dir+"/"+file, '//'.join(dir.split('\\')[:-1])+"/Comments_copy/"+file)

def get_index(lst=None, item=''):
    return [index for (index,value) in enumerate(lst) if value == item]

distinct("D:\Dataset\Douban")