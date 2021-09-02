import logging
import re
import time
import random
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup


if os.path.dirname(__file__):
    prefix=os.path.dirname(__file__)+"\\"
else:
    prefix=""
logging.basicConfig(level=logging.WARNING,  # 控制台打印的日志级别
                    filename=prefix+'movie_review.log',
                    filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
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


def get_movie_html(movie_id, start):
    headers = {
        'User-Agent': get_user_agent()
    }

    cookie_str=r'll="118371"; bid=OR_ri6ItpYc; __utmv=30149280.331; __yadk_uid=Tos4nxUPA3RJM69mnN5qmv0NZXlJKqnK; douban-fav-remind=1; douban-profile-remind=1; _vwo_uuid_v2=D484B29D396A2218A66ECDCCB1155BC0F|540ad863d03c0d21d0224a225089a18a; __gads=ID=8981b29009d8466b:T=1613288710:S=ALNI_MY0r3ZCtaMWd561iGLUYPwt54rfVA; gr_user_id=46f99f1d-ebf4-4e38-9a9e-39f5ad082e52; push_doumail_num=0; __utmz=30149280.1619527675.35.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); push_noty_num=0; ct=y; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1623080948%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.849814829.1609414876.1622721292.1623080949.42; __utmc=30149280; __utmt=1; ap_v=0,6.0; _pk_id.100001.8cb4=3bd33d64540e3a2e.1609414875.42.1623081038.1622721290.; __utmb=30149280.6.10.1623080949; dbcl2="3310037:GB7piuCaHXQ"; ck=AiVj'

    cookies=[]
    for line in cookie_str.split(';'):
        key,value=line.split('=',1)
        cookies[key] = value

    base_url = 'https://movie.douban.com/subject/{}/reviews?start={}'
    html = requests.get(base_url.format(movie_id, start), headers=headers, cookies=cookies).text
    time.sleep(7)
    return html


def save_reviews(movie_name, reviews, page):
    data = pd.DataFrame(reviews, columns=['review_rid', 'review_url', 'star_rating', 'uid',
                                          'name', 'review_pre', 'review_text', 'review_time',
                                          'review_useful_count', 'review_useless_count',
                                          'review_reply'])

    data.to_csv(prefix+'new_data\\' + movie_name + '.csv', mode='a', header=False, index=False, encoding='utf-8-sig')


def get_quantity_page(id):
    html = get_movie_html(id, '1')
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.string.strip()
    quantity_left = quantity_right = 0
    for i in range(len(title)):
        if title[i] == '(':
            quantity_left = i + 1
        elif title[i] == ')':
            quantity_right = i
    quantity = int(title[quantity_left:quantity_right])

    return quantity


def xunhuan(movie_id, now_page, xunhuantime):
    if xunhuantime >= 3:
        return ""
    try:
        movie_review_htmls = get_movie_html(movie_id, now_page)
        return movie_review_htmls
    except:
        xunhuan(movie_id, now_page, xunhuantime + 1)


def one_movie(movie_name, movie_id):
    # 获取 总数量
    quantity_page = get_quantity_page(movie_id)
    print(movie_name + "共" + str(quantity_page) + "篇")
    # 保证下次也从这爬取
    with open(prefix+'page.txt', encoding='utf-8-sig') as f:
        now_page = int(f.read())
    # 固定数量
    while now_page <= quantity_page:
        print(movie_name + ":开始爬取" + str(now_page) + "到" + str(now_page + 20) + "页")
        try:
            movie_review_htmls = get_movie_html(movie_id, now_page)
            # 访问成功直接保存新页
            with open(prefix+'page.txt', 'w', encoding='utf-8-sig') as f:
                f.write(str(now_page + 20))
        except Exception as e:
            logging.error(str(Exception) + '\n' + str(e))
            # 连续试试看
            movie_review_htmls = xunhuan(movie_id, now_page, 1)
            if movie_review_htmls == "":
                print(movie_name + ": 第" + str(now_page) + "到" + str(now_page + 20) + "篇爬取失败！")
        print(movie_name + ": 第" + str(now_page) + "到" + str(now_page + 20) + "篇爬取完成")
        # 把空格和回车去掉
        movie_review_htmls = movie_review_htmls.replace(" ", "")
        movie_review_htmls = movie_review_htmls.replace("\n", "")
        review_reply = re.findall('class="reply">(.*?)</a>', movie_review_htmls)
        # 力荐 5* 推荐 4* 还行 3* 较差 2* 很差 1*
        movie_review_htmls = re.findall('<headerclass="main-hd">(.*?)class="reply">.*?</a>', movie_review_htmls)
        # 需要的数据
        review_pre = []
        review_rid = []
        review_text_pre = []
        review_time = []
        review_url = []
        review_useful_count = []
        review_useless_count = []
        star_rating = []
        uid_and_name = []
        # 一个个保存
        for movie_review_html in movie_review_htmls:
            review_rid_1 = re.findall('class="review-short"data-rid="(.*?)">', movie_review_html)
            if len(review_rid_1) == 0:
                review_rid.append("None")
            else:
                review_rid.append(review_rid_1[0])
            review_url_1 = re.findall('<h2><ahref="(.*?)">.*?</a></h2>', movie_review_html)
            if len(review_url_1) == 0:
                review_url.append("None")
            else:
                review_url.append(review_url_1[0])
            star_rating_1 = re.findall('<spanclass="allstar(.*?)0main-title-rating"title=.*?"></span>',
                                       movie_review_html)
            if len(star_rating_1) == 0:
                star_rating.append("None")
            else:
                star_rating.append(star_rating_1[0])
            uid_and_name_1 = re.findall('</a><ahref="https://www.douban.com/people/(.*?)/"class="name">(.*?)</a>',
                                        movie_review_html)
            if len(uid_and_name_1) == 0:
                uid_and_name.append("None")
            else:
                uid_and_name.append(uid_and_name_1[0])
            review_time_1 = re.findall('class="main-meta">(.*?)</span>', movie_review_html)
            if len(review_time_1) == 0:
                review_time.append("None")
            else:
                review_time.append(review_time_1[0])
            review_pre_1 = re.findall('<ahref="https://movie.douban.com/review/.*?/">(.*?)</a></h2>', movie_review_html)
            if len(review_pre_1) == 0:
                review_pre.append("None")
            else:
                review_pre.append(review_pre_1[0])

            review_useful_count_1 = re.findall('<spanid="r-useful_count-.*?">(.*?)</span>', movie_review_html)
            if len(review_useful_count_1) == 0:
                review_useful_count.append("None")
            else:
                review_useful_count.append(review_useful_count_1[0])
            review_useless_count_1 = re.findall('<spanid="r-useless_count-.*?">(.*?)</span>', movie_review_html)
            if len(review_useless_count_1) == 0:
                review_useless_count.append("None")
            else:
                review_useless_count.append(review_useless_count_1[0])
            review_text_pre_1 = re.findall("<divclass=\"short-content\">(.*?)&nbsp;", movie_review_html)
            if len(review_text_pre_1) == 0:
                review_text_pre.append("None")
            else:
                review_text_pre.append(review_text_pre_1[0])

        review_text = []
        for i in review_text_pre:
            if "这篇影评可能有剧透" in i:
                review_text.append(str(i).replace("<pclass=\"spoiler-tip\">这篇影评可能有剧透</p>", "这篇影评可能有剧透"))
            else:
                review_text.append(i)
        uid = []
        name = []
        for i in uid_and_name:
            uid.append(i[0])
            name.append(i[1])
        reviews = {'review_rid': review_rid, 'review_url': review_url, 'star_rating': star_rating, 'uid': uid,
                   'name': name, 'review_pre': review_pre, 'review_text': review_text, 'review_time': review_time,
                   'review_useful_count': review_useful_count, 'review_useless_count': review_useless_count,
                   'review_reply': review_reply
                   }

        save_reviews(movie_name, reviews, now_page)
        now_page += 20
    # 将页数归零
    with open(prefix+'page.txt', 'w', encoding='utf-8-sig') as f:
        f.write(str(0))


def main():
    with open(prefix+'index.txt', 'r') as f:
        index = f.read()
    sleep_count = 1
    try:
        movie_id, movie_name = get_name_id()
        if len(movie_name) == 0 and len(movie_id) == 0:
            print("爬取结束！\n退出爬取！")
        for i in range(int(index), len(movie_name)):
            if sleep_count % 5 == 0:
                time.sleep(random.randint(600, 900))
            sleep_count += 1
            try:
                one_movie(movie_name[i], movie_id[i])
                print(movie_name[i] + "保存成功")
                with open(prefix+'index.txt', 'w') as f:
                    f.write(str(i + 1))
            except Exception as e:
                with open(prefix+'index.txt', 'w') as f:
                    f.write(str(i))
                logging.error(str(Exception) + '\n' + str(e))
                print("保存" + movie_name[i] + "失败！睡眠开始！")
                time.sleep(random.randint(7200, 12000))
                main()
            index = i
    except Exception as e:
        with open(prefix+'index.txt', 'w') as f:
            f.write(str(index))
        logging.error(str(Exception) + '\n' + str(e))
        print("爬取" + str(index) + "页失败，退出爬取！")
        return


if __name__ == '__main__':
    main()
