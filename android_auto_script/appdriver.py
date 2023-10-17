# -*- coding: UTF-8 -*-
import difflib
import os
from random import random
import re
import time
from adbdriver import *
from paddleocr import PaddleOCR
import cvimage
import json

class AppError(Exception): pass

class AppDriver():
    phone = None
    imgName = None
    srcDir = None
    dstDir = None
    appName = None
    appid = None
    stateCounter={}
    ocrRes = None
    screencapId = 0
    debug = True
    prevOcrRes = None

    def __init__(self) -> None:
        self.ocr = PaddleOCR(use_angle_cls=False, lang="ch")
        self.srcImg = self.srcDir + '/' + self.imgName
        self.dstImg = self.dstDir + '/' + self.imgName
        self.adb = AdbDriver('9879e031')
        # mkdir
        if not os.path.exists(self.dstDir):
            os.makedirs(self.dstDir)

    def makeScreenCap(self):
        if self.screencapId > 0 and self.debug and os.path.exists(self.dstImg):
            savedir = self.dstDir + '/debug_%d' % ((self.screencapId - 1) / 1000)
            saveName = '%d.jpg' % (self.screencapId - 1)
            if not os.path.exists(savedir): os.makedirs(savedir)
            os.system('copy /Y "%s" "%s"' % (self.dstImg.replace('/', '\\'), (savedir + '/' + saveName).replace('/', '\\')))
            saveName += '.txt'
            with open((savedir + '/' + saveName), "w", encoding='utf-8') as f:
                json.dump(self.ocrRes, fp=f, ensure_ascii=False)
        self.screencapId += 1
        self.adb.screenCap(self.srcImg)
        self.adb.pullFile(self.srcImg, self.dstImg)
        return os.path.exists(self.dstImg)

    def makeScreenCapGetTitleBarColor(self):
        self.makeScreenCap()
        return self.getCurrentImageMajorColor(0, 0, self.phone.w, self.phone.getTitleBarY1Y2()[1])
        
    def getCurrentImageMajorColor(self, l, t, w, h):
        img = cvimage.Image(self.dstImg)
        return img.getMajorColor(l, t, w, h)

    def makeScreenCapGetText(self, l=-1, t=-1, w=-1, h=-1):
        self.makeScreenCap()
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
        self.prevOcrRes = self.ocrRes
        self.ocrRes = txt
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

    def findTextItem(self, text):
        ocrRes = self.ocrRes
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

    def findAllTextItem(self, text):
        ocrRes = self.ocrRes
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

    def matchTextItem(self, text):
        ocrRes = self.ocrRes
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        cmpl = re.compile(text)
        for t in ocrRes:
            if cmpl.match(t[1][0]) != None:
                print('ocr match: ' + t[1][0])
                return OcrTextItem(t)
        return None

    def matchAllTextItem(self, text):
        ocrRes = self.ocrRes
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

    def findTextItemEx(self, callbackFunc):
        ocrRes = self.ocrRes
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

    def matchTextItemAtLeft(self, text, ft=0.25):
        ocrRes = self.ocrRes
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        cmpl = re.compile(text)
        w = self.phone.w * ft
        for t in ocrRes:
            if t[0][0][0] < w and cmpl.match(t[1][0]) != None:
                txtItem = OcrTextItem(t)
                return txtItem
            # else:
            #	print('skip: ' + t[1][0])
        return None

    def matchTextItemAtTop(self, text, ft=0.25):
        ocrRes = self.ocrRes
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        cmpl = re.compile(text)
        h = self.phone.h * ft
        for t in ocrRes:
            if t[0][0][1] < h and cmpl.match(t[1][0]) != None:
                txtItem = OcrTextItem(t)
                return txtItem
            # else:
            #	print('skip: ' + t[1][0])
        return None

    def matchTextItemAtRight(self, text, ft=0.75):
        ocrRes = self.ocrRes
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        cmpl = re.compile(text)
        r = self.phone.w * ft
        for t in ocrRes:
            if t[0][1][0] > r and cmpl.match(t[1][0]) != None:
                txtItem = OcrTextItem(t)
                return txtItem
            # else:
            #	print('skip: ' + t[1][0])
        return None

    def matchTextItemAtBottom(self, text, ft=0.75):
        ocrRes = self.ocrRes
        if ocrRes == None:
            return None
        #[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
        cmpl = re.compile(text)
        h = self.phone.h * ft
        for t in ocrRes:
            if t[0][1][1] > h and cmpl.match(t[1][0]) != None:
                txtItem = OcrTextItem(t)
                return txtItem
            # else:
            #	print('skip: ' + t[1][0])
        return None

    def getMatchCount(self, tags, matchFunc):
        n = 0
        for it in tags:
            if matchFunc(it) != None:
                n += 1
        return n

    def clickTextItemBySwide(self, txtItem):
        if txtItem == None:
            return
        xy = txtItem.getClickXY()
        self.adb.swipe(xy[0]-10, xy[1]-10, xy[0]+10, xy[1]+10, 50)

    def clickTextItemLeft(self, txtItem):
        if txtItem == None:
            return
        xy = txtItem.getLTRB()
        self.adb.click(xy[0]-10, xy[1])

    def swipeDown(self):
        fx = 3/6 + random() * 1/12
        fy = 1/8 + random() * 1/16
        x1, y1, x2, y2 = self.phone.w * fx, self.phone.h * fy, self.phone.w * fx, self.phone.h * (1-fy)
        self.adb.swipe(x1, y1, x2, y2)

    def swipeUp(self):
        fx = 3/6 + random() * 1/12
        fy = 1/8 + random() * 1/16
        x1, y1, x2, y2 = self.phone.w * fx, self.phone.h * fy, self.phone.w * fx, self.phone.h * (1-fy)
        self.adb.swipe(x2, y2, x1, y1)

    def swipeRight(self):
        fx = 1/6 + random() * 1/12
        fy = 4/8 + random() * 1/16
        x1, y1, x2, y2 = self.phone.w * fx, self.phone.h * fy, self.phone.w * (1-fx), self.phone.h * fy
        self.adb.swipe(x1, y1, x2, y2)

    def swipeLeft(self):
        fx = 1/6 + random() * 1/12
        fy = 4/8 + random() * 1/16
        x1, y1, x2, y2 = self.phone.w * fx, self.phone.h * fy, self.phone.w * (1-fx), self.phone.h * fy
        self.adb.swipe(x2, y2, x1, y1)

    def onStateChanged(self, stateName):
        cnt = 1
        #inc state
        if stateName in self.stateCounter:
            cnt = self.stateCounter[stateName] + 1
            self.stateCounter[stateName] = cnt
        else:
            self.stateCounter[stateName] = 1
        #clear other states
        for k in self.stateCounter:
            if k != stateName:
                self.stateCounter[k] = 0
        print('ON_STATE_CHANGED -> %s [%d]' % (stateName, cnt))
        return cnt

    def isScreenTextNotChanged(self):
        if self.prevOcrRes == None or self.ocrRes == None:
            return False
        prevText, currText = '', ''
        for it in sorted(self.prevOcrRes):
            prevText += it[1][0]
        for it in sorted(self.ocrRes):
            currText += it[1][0]
        
        return difflib.SequenceMatcher(None, prevText, currText).quick_ratio() > 0.95

    def goHome(self):
        self.adb.goBackN(10)
        self.adb.goHome()
        self.adb.forceStop(self.appid)
