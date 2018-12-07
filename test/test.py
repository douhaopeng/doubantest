from urllib import request
import pymysql
import pandas as pd
import jieba
import requests
from bs4 import BeautifulSoup
import urllib.request
import re
import numpy as np
import time
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import csv
import matplotlib.pyplot as plt


def dl():
    loginUrl = 'https://accounts.douban.com/login'
    formData = {
        "redir": "http://movie.douban.com/mine?status=collect",
        "form_email": '2534517355@qq.com',
        "form_password": 'gzy123456',
        "login": u'登录'
    }
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}
    r = requests.post(loginUrl, data=formData, headers=headers)
    page = r.text
    '''获取验证码图片'''
    # 利用bs4获取captcha地址
    soup = BeautifulSoup(page, "html.parser")
    captchaAddr = soup.find('img', id='captcha_image')['src']
    # 利用正则表达式获取captcha的ID
    reCaptchaID = r'<input type="hidden" name="captcha-id" value="(.*?)"/'
    captchaID = re.findall(reCaptchaID, page)
    # 保存到本地
    urllib.request.urlretrieve(captchaAddr, "captcha.jpg")
    captcha = input('please input the captcha:')

    formData['captcha-solution'] = captcha
    formData['captcha-id'] = captchaID
    session = requests.session()
    r = session.post(loginUrl, data=formData, headers=headers)
    page = r.text
    print(r.url)
    if r.url == 'https://movie.douban.com/mine?status=collect':
        print('Login successfully!!!')
        print('我看过的电影', '-' * 60)
    else:
        print("failed!")
    return session


#https://movie.douban.com/subject/3168101/comments?status=P
#https://movie.douban.com/subject/3168101/comments?start=20&limit=20&sort=new_score&status=P
def jiexi(url,session):
    comment =[]
    resp = session.get(url)
    content = resp.text
    str1 ='<span.*?class=\"short[\\s]*\".*?</span>'
    str2 = re.compile(str1)
    list =  re.findall(str2,content)
    for item in list:
        str3 = '>(.*?)<'
        str4 = re.compile(str3)
        yp = re.findall(str4,item)[0]
        comment.append(yp)
    return comment


def jiexi2(session):
    comments = []
    comment2 = []
    for i in range(0,26):
        url = 'https://movie.douban.com/subject/3168101/comments?start=%d&limit=20&sort=new_score&status=P' % (i * 20)
        comment = jiexi(url,session)
        time.sleep(1)
        comment2.append(comment)
        print(url)
    for i in comment2:
        for j in i:
            comments.append(j)
    return comments


def jiexi3(session):
    comments = []
    comment2 = []
    for i in range(0,26):
        url = 'https://movie.douban.com/subject/3168101/comments?start=%d&limit=20&sort=new_score&status=P' % (i * 20)
        comment = jiexi(url,session)
        time.sleep(1)
        comment2.append(comment)
    for i in comment2:
        for j in i:
            comments.append(j)
    return comments


def connectDB():
    mydb = pymysql.connect(
        host='localhost',
        user='root',
        passwd='123456',
        database='yingping'
    )
    return mydb


def insertData(session):
    #调用函数拿到数据
    comments=jiexi3(session)
    # print(len(comments))
    sql= 'insert into yingping (comment) values (%s)'
    db=connectDB()
    #获取cursor对象
    cursor=db.cursor()
    index=0
    for item in comments:
        info=(item)
        cursor.execute(sql,info)
        db.commit()
        index+=1
    # print(index)
    cursor.close()
    db.close()
    print("数据库存储完毕")
    pass


def data_write_csv(session):
   comments = jiexi2(session)
   test = pd.DataFrame(data=comments)
   test.to_csv('test.csv',index=0,header=0)


def getDataFromCSV():
    comments = []
    with open('test.csv', 'r', encoding='utf-8') as f:
        # 获取到读得对象，内容在这个对象里
        reader = csv.reader(f)
        # 遍历这个对象
        for item in reader:
                # 将每一条数据添加到列表中
            comments.append(item)
        f.close()
        pass
    return comments
    pass


def getWordCloud():
    #拿到我们做词云的所有的数据
    data=getDataFromCSV()
    comments=''
    for item in data:
        for i in item:
        #把所有的评论放在一个字符串中
            comments+=i
    #通过jieba分词把字符串分成一个个的词语，然后词语之间用’ ‘隔开，连接在一起
    cut_word=' '.join(jieba.cut(comments))
    #读取图片，然后用numpy处理
    bgImage=np.array(Image.open('li.png'))
    wordCloud=WordCloud(
        font_path='C:/Windows/Fonts/STXINGKA.TTF',
        background_color='white',
        mask=bgImage
    ).generate(cut_word)
    #保存成图片
    image_colors = ImageColorGenerator(bgImage)
    plt.imshow(wordCloud)
    plt.axis('off')
    plt.show()
    # 保存成图片
    wordCloud.to_file('test.png')
    pass


def start():
    session= dl()
    data_write_csv(session)
    getWordCloud()
    connectDB()
    insertData(session)


if __name__ == '__main__':
    start()