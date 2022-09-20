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
    tagLingJinBi = ['金币收益', '现金收益', '日常任务']

    def __init__(self) -> None:
        self.phone = screen.SamSungNote4()
        self.imgName = 'screen.png'
        self.srcDir = '/sdcard/Pictures'
        self.dstDir = 'H:/douyin'
        self.appName = '抖音极速版'
        super().__init__()

    def isAtMainPage(self):
        txt = self.loopUntilTextMatch(self.tagMain, 1)
        guanzhu = matchTextItem(txt, self.tagMain[0])
        tuijian = findTextItem(txt, self.tagMain[1])
        if tuijian == None:
            tuijian = findTextItem(txt, self.tagMain[2])
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
            txt = self.loopUntilTextFound(it, 2)
            if txt != None:
                print('关掉青少年模式')
                txtItem = findTextItem(txt, popupinfo[it])
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
            txt = self.loopUntilTextFound(self.tagLingJinBi, 5)
            if txt == None:
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
        txt = self.loopUntilTextFound([self.appName])
        txtItem = findTextItem(txt, self.appName)
        pt = txtItem.getClickPoint()
        self.adb.click(pt.x, pt.y)
        time.sleep(2)

        print('等待进入主页')
        self.loopUntilVideoTapFound()
        time.sleep(5)

        print('进入金币界面')
        if not self.tryEnterLingJinBi():
            raise (Exception("进入金币界面-失败"))

        self.autoWatchAd()

    def waitVideo(self):
        tag=['.*s后可领奖励', '领取成功']

    def watchMeiRiQianDao(self, txt):
        txtItem = findTextItem(txt, '每日签到')
        if txtItem == None:
            return False

        txtItem = matchTextItem(txt, '立即签到.*')
        if txtItem != None:
            pt = txtItem.getClickPoint()
            self.adb.click(pt.x, pt.y)
        time.sleep(5)

        txt = self.loopUntilTextMatch(['签到成功.*'], 5)
        txtItem = matchTextItem(txt, '看广告视频再赚.*')
        if txtItem != None:
            pt = txtItem.getClickPoint()
            self.adb.click(pt.x, pt.y)
        
        self.waitVideo()
        return True

    def autoWatchAd(self):
        while True:
            time.sleep(5)
            txt = self.makeScreenCapGetText()
            if self.watchMeiRiQianDao(txt):
                continue

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
