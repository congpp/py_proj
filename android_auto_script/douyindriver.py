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
        self.dstDir = 'H:/douyin'
        self.appName = '抖音极速版'
        super().__init__()

    def isAtMainPage(self):
        ocrRes = self.loopUntilTextMatch(self.tagMain, 1)
        guanzhu = self.matchTextItem(ocrRes, self.tagMain[0])
        tuijian = self.findTextItem(ocrRes, self.tagMain[1])
        if tuijian == None:
            tuijian = self.findTextItem(ocrRes, self.tagMain[2])
        if tuijian != None and guanzhu != None and guanzhu.isHorizontalAlignWith(tuijian, self.phone.height() * 0.05):
            print('首页已进入')
            return True
        return False

    def loopUntilVideoTapFound(self):
        for i in range(0, 5):
            if self.isAtMainPage():
                return True
            time.sleep(5)
        return False

    def closeAllPopup(self, popupinfo):
        for it in popupinfo:
            ocrRes = self.loopUntilTextFound(it, 2)
            if ocrRes != None:
                print('关掉-' + it)
                txtItem = self.findTextItem(ocrRes, popupinfo[it])
                pt = txtItem.getClickPoint()
                self.adb.click(pt.x, pt.y)
                time.sleep(2)

    def closeAllPopupInMain(self):
        popupinfo = {
            '青少年模式': '我知道了'
        }
        self.closeAllPopup(popupinfo)

    def tryEnterLingJinBi(self):
        for i in range(1, 5):
            if self.isAtMainPage():
                print('点击钱包位置')
                x = self.phone.width() / 2
                y = self.phone.getBottomBarY()
                self.adb.click(x, y)

            time.sleep(5)
            print('尝试进入金币界面')
            ocrRes = self.loopUntilTextFound(self.tagLingJinBi, 5)
            if ocrRes == None:
                print('领金币进入失败，尝试关掉所有弹框')
                self.closeAllPopupInMain()
                continue

            return True

        return False

    def goHomeAndStartApp(self):
        print('回到桌面')
        self.adb.goHomeByGoBack(10)
        time.sleep(2)

        print('找到并打开app')
        ocrRes = self.loopUntilTextFound([self.appName])
        txtItem = self.findTextItem(ocrRes, self.appName)
        self.adb.click(txtItem.getClickXY())
        time.sleep(2)

        print('等待进入主页')
        self.loopUntilVideoTapFound()
        time.sleep(5)

        print('进入金币界面')
        if not self.tryEnterLingJinBi():
            raise (Exception("进入金币界面-失败"))

        self.autoWatchAd()

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

    def handleTaskItem(self, ocrRes, titletxt, btnTxt):
        titles = self.matchAllTextItem(ocrRes, titletxt)
        btns = self.matchAllTextItem(ocrRes, btnTxt)
        if titles == None or btns == None:
            return False
        
        for t in titles:
            for b in btns:
                if t.isHorizontalAlignWith(b):
                    self.adb.click(b.getClickXY())
                    self.waitVideo()
                    return True
        return False


    def isAtLingJinBiPage(self, ocrRes):
        print('isAtLingJinBiPage')
        txtItem = self.findTextItemEx(ocrRes, lambda t: t.text in self.tagLingJinBi)
        if txtItem != None:
            print('当前在领金币页面')
            return True
        txtItem = self.findTextItemEx(ocrRes, lambda t: t.text == '赚钱任务' and t.getClickXY()[1] < self.phone.h * 0.125)
        if txtItem != None:
            print('当前在领金币页面')
            return True
        print('不在领金币页面')
        return False

    #自动做任务
    def autoWatchAd(self):
        upOrDown = 0
        print('autoWatchAd')
        while True:
            time.sleep(10)
            ocrRes = self.makeScreenCapGetText()
            if self.handleMeiRiQianDaoPopup(ocrRes):
                continue
            elif self.handleQianDao(ocrRes):
                continue
            elif self.handleVideoAgainPopup(ocrRes):
                continue
            elif self.handleVideoAgainPopup(ocrRes):
                continue
            elif not self.isAtLingJinBiPage(ocrRes):
                self.adb.goBack()
                continue
            elif self.handleTaskItem(ocrRes, '看广告赚金币', '去领取'):
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
