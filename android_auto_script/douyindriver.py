# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from adbdriver import *
from paddleocr import PaddleOCR
import appdriver
import screen
import cvimage
import cv2


class DouYinDriver(appdriver.AppDriver):

    tagMain = ['关注.{0,6}', '推荐', '精选']
    tagLingJinBi = ['金币收益', '现金收益']
    titleBarClrOfLingJinBi = [113,80,255]

    def __init__(self) -> None:
        self.phone = screen.SamSungNote4()
        self.imgName = 'screen.png'
        self.srcDir = '/sdcard/Pictures'
        self.dstDir = 'd:/cyc/douyin'
        self.appName = '抖音极速版'
        super().__init__()

    def isAtDesktop(self):
        tags={'联系人', '信息', '浏览器', '应用程序'}
        #至少匹配3个
        while len(tags) >= 1:
            for it in tags:
                if self.matchTextItemAtBottom(it) != None:
                    tags.remove(it)
                    break
        return len(tags) <= 1

    def onAtDesktop(self):
        cnt = self.onStateChanged('desktop')
        if cnt > 1:
            txtItem = self.matchTextItem(self.appName)
            if txtItem != None:
                self.adb.click(txtItem)
                self.onStateChanged('none')

    def isAtMainPage(self): 
        tags={'首页', '朋友', '消息.{0,3}', '我.{0,3}'}
        #至少匹配三个
        while len(tags) >= 1:
            for it in tags:
                if self.matchTextItemAtBottom(it) != None:
                    tags.remove(it)
                    break
        return len(tags) <= 1

    def onMainPage(self):
        print('点击钱包位置')
        x = self.phone.width() / 2
        y = self.phone.getBottomBarY()
        self.adb.click(x, y)
        self.onStateChanged('none')

    def isAtQingShaoNianMoShi(self):
        tags={'青少年模式', '我知道了', '开启青少年.*'}
        #至少匹配2个
        while len(tags) >= 1:
            for it in tags:
                if self.matchTextItemAtBottom(it) != None:
                    tags.remove(it)
                    break
        return len(tags) <= 1

    def onQingShaoNianMoShi(self):
        cnt = self.onStateChanged('qigshaonian')
        if cnt > 1:
            txtItem = self.matchTextItem('我知道了')
            if txtItem != None:
                self.adb.click(txtItem)
                self.onStateChanged('none')

    def isAtLingJinBiPage(self):
        print('isAtLingJinBiPage')
        txtItem = self.makeScreenCapGetTitleBarColor()
        if txtItem != None:
            print('当前在领金币页面')
            return True
        txtItem = self.findTextItemEx(lambda t: t.text == '赚钱任务' and t.getClickXY()[1] < self.phone.h * 0.125)
        if txtItem != None:
            print('当前在领金币页面')
            return True
        print('不在领金币页面')
        return False

    def onLingJinBi(self):
        pass

    #等待广告视频播完
    def waitVideo(self):
        print('waitVideo')
        time.sleep(40)
        tag=['.*s后可领奖励']
        self.loopUntilTextNotMatch(tag, 10, t=0, h=self.phone.height() / 6)
        print('广告视频已经看完')
        self.adb.goBack()
        time.sleep(10)
        for i in range(2):
            if self.loopUntilTextNotFound(['领取成功']):
                break
            time.sleep(10)
        return True

    #继续看视频
    def watchVideoAgain(self, ocrRes, titletxt, btntxt):
        print('watchVideoAgain: %s %s' % (titletxt, btntxt))
        txtItem = self.matchTextItem(ocrRes, titletxt)
        if txtItem == None:
            print('没有弹出-' + titletxt)
            return False
        
        txtItem = self.matchTextItem(ocrRes, btntxt)
        if txtItem == None:
            print('没有找到弹窗 %s 的按钮 %s' % (titletxt, btntxt))
            return False
        self.adb.click(txtItem.getClickXY())
        self.waitVideo()
        return True
        
    #继续看视频
    def handleVideoAgainPopup(self, ocrRes):
        print('handleVideoAgainPopup')
        tag={'看广告视频再赚.*':'看广告视频再赚.*', '再看一个视频额外获得.*':'领取奖励'}
        for it in tag:
            if self.watchVideoAgain(ocrRes, it, tag[it]):
                return True
        return False

    #每日签到弹框
    def handleMeiRiQianDaoPopup(self, ocrRes):
        print('handleMeiRiQianDaoPopup')
        txtItem = self.findTextItem(ocrRes, '每日签到')
        if txtItem == None:
            return False

        txtItem = self.matchTextItem(ocrRes, '立即签到.*')
        if txtItem != None:
            self.adb.click(txtItem.getClickXY())
        time.sleep(10)

        ocrRes = self.loopUntilTextMatch(['签到成功.*'], 5)
        txtItem = self.matchTextItem(ocrRes, '看广告视频再赚.*')
        if txtItem != None:
            self.adb.click(txtItem.getClickXY())
        
        self.waitVideo()
        return True

    #签到
    def handleQianDao(self, ocrRes):
        print('handleQianDao')
        txtItem = self.findTextItemEx(ocrRes, lambda txtItem: txtItem.text=='签到' and txtItem.getClickXY()[0] > self.phone.width() * 2 / 3)
        if txtItem == None:
            txtItem = self.findTextItemEx(ocrRes, lambda txtItem: txtItem.text=='已签到' and txtItem.getClickXY()[0] > self.phone.width() * 2 / 3)
            if txtItem != None:
                print(txtItem.text)
            return False

        self.adb.click(txtItem.getClickXY())
        time.sleep(10)

        ocrRes = self.loopUntilTextMatch(['签到成功.*'], 5)
        txtItem = self.matchTextItem(ocrRes, '看广告视频再赚.*')
        if txtItem != None:
            ltrb = txtItem.getLTRB()
            self.adb.click(ltrb[0]-10, ltrb[1])
        
        self.waitVideo()
        return True

    def handleTaskItem(self, titletxt, btnTxt):
        titles = self.matchAllTextItem(titletxt)
        btns = self.matchAllTextItem(btnTxt)
        if titles == None or btns == None:
            return False
        
        for t in titles:
            for b in btns:
                if t.isHorizontalAlignWith(b):
                    self.adb.click(b.getClickXY())
                    self.waitVideo()
                    return True
        return False

    #运行
    def run(self):
        cnt = 1
        upOrDown = 0
        while True:
            print('\n================= run %d =================\n' % (cnt))
            cnt += 1
            time.sleep(15)
            ocrRes = self.makeScreenCapGetText()
            if self.isAtDesktop():
                self.onAtDesktop()
                continue
            elif self.isAtQingShaoNianMoShi():
                self.onQingShaoNianMoShi()
                continue
            elif self.handleVideoAgainPopup():
                continue
            elif self.handleVideoAgainPopup():
                continue
            elif not self.isAtLingJinBiPage():
                self.adb.goBack()
                continue
            elif self.handleTaskItem('看广告赚金币', '去领取'):
                continue
            else:
                upOrDown+=1
                if upOrDown < 5:
                    self.scrollUp()
                elif upOrDown < 10:
                    self.scrollDown()
                else:
                    upOrDown = 0

    def start(self):
        print('drive starts')
        self.goHomeAndStartApp()


def main():
    douyin = DouYinDriver()
    if sys.argv[1].lower() == '-c':
        douyin.autoWatchAd()
    else:
        douyin.start()


if __name__ == '__main__':
    main()
