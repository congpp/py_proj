# -*- coding: UTF-8 -*-

#爬取filesignature.net，存储成 文件描述 后缀 标识头
#https://filesignatures.net/index.php?page=all&order=EXT&alpha=All&currentpage=1
#selenium + chromedriver

from pyquery import PyQuery as pq

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import re
import os
import random
import codecs

savefile = codecs.open('./filesig.txt','w','utf-8')
chrome_options = Options()
#chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(browser, 10)

#'http://www.kugou.com/yy/singer/index/2-all-1.html'
def openUrlByChrome(url):
    print('open url %s'%(url))
    browser.get(url)
    wait = WebDriverWait(browser, 10)


def parsedata():
    html = browser.page_source
    doc = pq(html)
    sigs = doc('table#innerTable tbody tr:gt(0) td:gt(0)').items()
    i=0
    for sig in sigs:
        savefile.write(sig.text())
        savefile.write(';')
        i = i+1
        if i%3 == 0:
            savefile.write('\n');


# def savedata(d):
    # for i in d:
        


if __name__ == '__main__':
    for i in range(1, 19):
        #'https://filesignatures.net/index.php?page=all&order=EXT&alpha=All&currentpage=1'
        url = 'https://filesignatures.net/index.php?page=all&order=EXT&alpha=All&currentpage={page}'.format(page=i)
        openUrlByChrome(url)
        parsedata()
        if i > 1:
            ActionChains(browser).key_down(Keys.CONTROL).send_keys("w").key_up(Keys.CONTROL).perform()
    browser.close()
