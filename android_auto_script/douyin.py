# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from xml.etree.ElementPath import findtext
from adbdriver import *
from paddleocr import PaddleOCR, draw_ocr
import cvimage
import cv2

SCREEN_WIDTH=540
SCREEN_HEIGHT=960

class DouYinDriver():
    def __init__(self) -> None:
        self.appName = '抖音极速版'
        self.ocr = PaddleOCR(use_angle_cls=False, lang="ch")
        self.imgName='screen.png'
        self.srcImg = '/sdcard/Pictures/' + self.imgName
        self.dstDir = 'H:/douyin'
        self.dstImg = self.dstDir + '/' + self.imgName
        self.adb = AdbDriver()
        #mkdir
        if not os.path.exists(self.dstDir):
            os.mkdir(self.dstDir)

    def makeScreenCapGetText(self):
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        #img = cvimage.Image(self.dstImg)
        txt = self.ocr.ocr(self.dstImg)
        print(txt)
        return txt
        
    def makeScreenCapGetTextVertical(self, t, h):
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        img = cvimage.Image(self.dstImg)
        c = img.cropVertical(t, h)
        txt = self.ocr.ocr(c)
        print(txt)
        return txt

    def makeScreenCapGetTextHorizontal(self, l, w):
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        img = cvimage.Image(self.dstImg)
        c = img.cropHorizontal(l, w)
        txt = self.ocr.ocr(c)
        print(txt)
        return txt

    def loopUntilTextFound(self, text, repeats=10):
        for i in range(0,repeats):
            txt = self.makeScreenCapGetText()
            for it in text:
                item = findTextItem(txt, it)
                if item != None:
                    return txt
            print('loop continues:' + str(text))
            time.sleep(5)
        return None

    def goHomeAndStartApp(self):
        print('回到桌面')
        self.adb.goHome()
        time.sleep(2)
        print('找到并打开app')
        txt = self.loopUntilTextFound([self.appName])
        txtItem = findTextItem(txt, self.appName)
        pt = txtItem.getClickPoint()
        self.adb.click(pt.x, pt.y)
        time.sleep(2)
        print('等待进入主页')
        txt = self.loopUntilTextFound(['关注', '推荐', '天河'])
        time.sleep(5)
        print('关掉青少年模式')
        txt = self.loopUntilTextFound(['青少年模式'], 2)
        if txt != None:
            txtItem = findTextItem(txt, '我知道了')
            pt = txtItem.getClickPoint()
            self.adb.click(pt.x, pt.y)
            time.sleep(2)
        print('进入金币界面')
        #txt = self.loopUntilTextFound(['朋友', '消息', '开宝箱'])
        #myfriend = findTextItem(txt, '朋友').getClickPoint()
        #mymsg = findTextItem(txt, '消息').getClickPoint()
        x = SCREEN_WIDTH / 2
        y = SCREEN_HEIGHT - 20
        self.adb.click(x, y)
        self.autoWatchAd()

    def autoWatchAd(self):
        pass

    def run(self):
        print('drive starts')
        self.goHomeAndStartApp()

def main():
    try:
        douyin = DouYinDriver()
        douyin.run()
    except Exception as e:
        raise e

if __name__ == '__main__':
	main()
