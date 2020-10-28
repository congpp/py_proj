#爬取酷狗官网所有歌手的名字、介绍、图片
#http://www.kugou.com/yy/singer/index/2-all-1.html
#selenium + chromedriver
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import re
import requests
import os
import random
import pymysql

db = pymysql.connect("192.168.1.146", "root", "", port=3306, db='test_db', charset='utf8')
cursor = db.cursor()
table = 'singer_info'
chrome_options = Options()
#chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(browser, 10)

#'http://www.kugou.com/yy/singer/index/2-all-1.html'
def openUrlByChrome(url):
    print('open url %s'%(url))
    browser.get(url)
    wait = WebDriverWait(browser, 10)


def findhref():
    html = browser.page_source
    doc = pq(html)
    li = doc.remove('.pic').find('.r ul li a').items()
    for i in li:
        yield i.attr('href')


def parsedata(d):
    for i in findhref():
        print(i)
        html = requests.get(i).text
        doc = pq(html)
        title = doc('body > div.wrap.clear_fix > div.sng_ins_1 > div.top > div > div > strong').text()
        des = doc('body > div.wrap.clear_fix > div.sng_ins_1 > div.top > div > p').text()
        img_url = doc('body > div.wrap.clear_fix > div.sng_ins_1 > div.top > img').attr('_src')
        data = {
            'name': title[0:127],
            'description': des[0:1023],
            'image': img_url[0:255]
        }
        print('name=%s desc=%s image=%s'%(title, des[0:10], img_url));
        d.append(data)


def download_image(url):
    file_path = None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            reg = re.search('(\d+)((\.jpg)|(\.png))$', url)
            file_path = reg.group(0)
            if not os.path.exists(file_path):
                with open(file_path, 'wb')as f:
                    f.write(response.content)
            else:
                print('Already downloaded!!!')
            return file_path
    except requests.ConnectionError:
        print("Downloading failed!!!")


def savetoMysql(data):
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    sql2 = 'INSERT INTO {table}({keys}) values ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql2, tuple(data.values())):
            print('success')
            db.commit()
    except Exception as e:
        print('erro', repr(e))
        db.rollback()


def savedata(d):
    for i in d:
        filepath = download_image(i.pop('image'))
        if(filepath):
            i['image']=filepath
            savetoMysql(i)


if __name__ == '__main__':
    d = []
    if not os.path.exists('img'):
        os.mkdir('img')
    os.chdir('img')
    letters=[]
    for i in range(ord('a'), ord('z')):
        letters.append(chr(i))
    letters.append('null')
    for i in letters:
        for j in range(1, 6):
            url = 'http://www.kugou.com/yy/singer/index/{page}-{letter}-1.html'.format(page=j, letter=i)
            openUrlByChrome(url)
            parsedata(d)
            savedata(d)
            d=[]
    browser.close()
