# -*- coding: UTF-8 -*-
import os
from random import random
import re
import time
from adbdriver import *
from paddleocr import PaddleOCR
import cvimage


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
        # mkdir
        if not os.path.exists(self.dstDir):
            os.mkdir(self.dstDir)

    def makeScreenCapGetTitleBarColor(self):
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        img = cvimage.Image(self.dstImg)
        x, y = self.phone.w/2, self.phone.getTitleBarY()
        rgb = img[y][x]

    def makeScreenCapGetText(self, l=-1, t=-1, w=-1, h=-1):
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        if l >= 0 and t >= 0 and w >= 0 and h >= 0:
            img = cvimage.Image(self.dstImg)
            c = img.crop(l, t, w, h)
            txt = self.ocr.ocr(c)
        elif l >= 0 and w >= 0:
            img = cvimage.Image(self.dstImg)
            c = img.cropHorizontal(l, w)
            txt = self.ocr.ocr(c)
        elif t >= 0 and h >= 0:
            img = cvimage.Image(self.dstImg)
            c = img.cropHorizontal(l, w)
            txt = self.ocr.ocr(c)
        else:
            #img = cvimage.Image(self.dstImg)
            txt = self.ocr.ocr(self.dstImg)
        # print(txt)
        return txt

    def loopUntilTextFound(self, text, repeats=10, l=-1, t=-1, w=-1, h=-1):
        for i in range(repeats):
            txt = self.makeScreenCapGetText(l, t, w, h)
            for it in text:
                item = self.findTextItem(txt, it)
                if item != None:
                    return txt
            print('loop continues:' + str(text))
            time.sleep(5)
        return None

    def loopUntilTextMatch(self, text, repeats=10, l=-1, t=-1, w=-1, h=-1):
        for i in range(repeats):
            txt = self.makeScreenCapGetText(l, t, w, h)
            for it in text:
                item = self.matchTextItem(txt, it)
                if item != None:
                    return txt
            print('loop continues:' + str(text))
            time.sleep(5)
        return None

    def loopUntilTextNotFound(self, text, repeats=10, l=-1, t=-1, w=-1, h=-1):
        for i in range(repeats):
            txt = self.makeScreenCapGetText(l, t, w, h)
            allGone = True
            for it in text:
                item = self.findTextItem(txt, it)
                if item != None:
                    allGone = False
                    break
            if allGone == False:
                print('loop continues:' + str(text))
                time.sleep(5)
            else:
                return True
        return False

    def loopUntilTextNotMatch(self, text, repeats=10, l=-1, t=-1, w=-1, h=-1):
        for i in range(repeats):
            txt = self.makeScreenCapGetText(l, t, w, h)
            allGone = True
            for it in text:
                item = self.matchTextItem(txt, it)
                if item != None:
                    allGone = False
                    break
            if allGone == False:
                print('loop continues:' + str(text))
                time.sleep(5)
            else:
                return True
        return False

    def findTextItem(self, ocrRes, text):
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        for t in ocrRes:
            if t[1][0] == text:
                print('ocr find: ' + t[1][0])
                return OcrTextItem(t)
            # else:
            #	print('skip: ' + t[1][0])
        return None

    def findAllTextItem(self, ocrRes, text):
        if ocrRes == None:
            return None
        res = []
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        for t in ocrRes:
            if t[1][0] == text:
                print('ocr find: ' + t[1][0])
                res.append(OcrTextItem(t))
            # else:
            #	print('skip: ' + t[1][0])
        return res

    def matchTextItem(self, ocrRes, text):
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        cmpl = re.compile(text)
        for t in ocrRes:
            if cmpl.match(t[1][0]) != None:
                print('ocr match: ' + t[1][0])
                return OcrTextItem(t)
        return None

    def matchAllTextItem(self, ocrRes, text):
        if ocrRes == None:
            return None
        res = []
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        cmpl = re.compile(text)
        for t in ocrRes:
            if cmpl.match(t[1][0]) != None:
                print('ocr match: ' + t[1][0])
                res.append(OcrTextItem(t))
        return res

    def findTextItemEx(self, ocrRes, callbackFunc):
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        for t in ocrRes:
            txtItem = OcrTextItem(t)
            if callbackFunc(txtItem):
                print('ocr find: ' + t[1][0])
                return txtItem
            # else:
            #	print('skip: ' + t[1][0])
        return None

    def scrollDown(self):
        fx = random()
        x1, y1, x2, y2 = self.phone.w * fx, self.phone.h - \
            300 * fx, self.phone.w * (1-fx), 300 * fx
        self.adb.swipe(x1, y1, x2, y2)

    def scrollUp(self):
        fx = random()
        x1, y1, x2, y2 = self.phone.w * fx, self.phone.h - \
            300 * fx, self.phone.w * (1-fx), 300 * fx
        self.adb.swipe(x2, y2, x1, y1)
