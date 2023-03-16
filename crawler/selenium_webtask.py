from selenium import webdriver
from browsermobproxy import Server
import time
import json
import psutil
import os
from wevwnd import *

class SeleniumWebTask:
    PATH_PROXY = r'toolset\browsermob\bin\browsermob-proxy.bat'
    PATH_CHROMIUM_DRIVER = r'toolset\chromium\chromedriver.exe'
    def __init__(self, msgSender: MsgSender, port: int = 9200) -> None:
        self.msgSender = msgSender
        self.__startProxy(port)

    def __del__(self)->None:
        self.__stopProxy()

    def __startProxy(self, port: int=9200) -> None:
        self.server = Server(path = SeleniumWebTask.PATH_PROXY, options={'port':port})
        self.server.start()
        self.proxy = self.server.create_proxy()

    def __stopProxy(self):
        if (self.server != None):
            self.server.stop()
            self.server = None
        #kill everything under java path
        pwd = os.path.split(os.path.realpath(__file__))[0]
        javapath = (pwd + r'\toolset\jdk1.8.0_181\bin').lower()
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
                exe = p.exe().lower()
                if exe.find(javapath) == 0:
                    p.kill()
            except:
                pass

    def restartProxy(self, port: int = 9200) -> None:
        self.__stopProxy()
        self.__startProxy(port)

    def openWebPage(self, url: str, timeout: int = 30) -> dict:
        # Options
        self.options = webdriver.ChromeOptions()
        #self.options.add_argument('--headless') # 开启无界面模式
        #self.options.add_argument('--disable-gpu') # 禁用显卡
        #self.options.add_argument('blink-settings=imagesEnabled=false')
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36") # 替换UA
        self.options.add_argument('--ignore-certificate-errors')
        print('using proxy: ' + self.proxy.proxy)
        self.options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
        self.options.add_argument('window-size=800,600')
        # self.options.add_argument('start-fullscreen')
        # self.options.add_argument('kiosk') 


        self.driver = webdriver.Chrome(executable_path = SeleniumWebTask.PATH_CHROMIUM_DRIVER, options=self.options)
        self.driver.set_page_load_timeout(timeout)

        self.proxy.new_har(options={'captureHeaders': True, 'captureContent': True,})
        self.driver.get(url)
        #time.sleep(10)

    def getNetworkElements(self):
        result = self.proxy.har
        with open('Networks.js', 'w', encoding='utf-8') as f:
            f.write(json.dumps(result['log']['entries'], indent=2))
        return result['log']['entries']

    def closeWebPage(self):
        self.driver.quit()

class SeleniumWebTaskMsgHandler(MsgHandler):
    def __init__(self, wt: SeleniumWebTask) -> None:
        self.wt = wt
        self.handlers = dict()
        self.handlers['openwebpage'] = self.onOpenWebPage
        self.handlers['closewebpage'] = self.onCloseWebPage

    def onOpenWebPage(self, data: dict):
        print('webtask open webpage: ' + data['url'])
        self.wt.openWebPage(data['url'])

    def onCloseWebPage(self):
        self.wt.closeWebPage()

    def handleMessage(self, msg: str, data: dict) -> dict:
        if msg not in self.handlers:
            return None
        self.handlers[msg](data)
            
        