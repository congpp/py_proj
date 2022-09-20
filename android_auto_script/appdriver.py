# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from adbdriver import *
from paddleocr import PaddleOCR
import screen
import cvimage
import cv2

class AppDriver():
    phone = None
    imgName = None
    srcDir = None
    dstDir = None
    appName = None
    def __init__(self) -> None:
        self.ocr = PaddleOCR(use_angle_cls=False, lang="ch")
        self.srcImg = self.srcDir + '/' + self.imgName
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
        #print(txt)
        return txt
        
    def makeScreenCapGetTextVertical(self, t, h):
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        img = cvimage.Image(self.dstImg)
        c = img.cropVertical(t, h)
        txt = self.ocr.ocr(c)
        #print(txt)
        return txt

    def makeScreenCapGetTextHorizontal(self, l, w):
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        img = cvimage.Image(self.dstImg)
        c = img.cropHorizontal(l, w)
        txt = self.ocr.ocr(c)
        #print(txt)
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

    def loopUntilTextMatch(self, text, repeats=10):
        for i in range(0,repeats):
            txt = self.makeScreenCapGetText()
            for it in text:
                item = matchTextItem(txt, it)
                if item != None:
                    return txt
            print('loop continues:' + str(text))
            time.sleep(5)
        return None
