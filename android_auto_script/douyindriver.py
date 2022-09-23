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


STATE_DESKTOP = 'desktop'
STATE_MAIN = 'main'
STATE_QINGSHAONIANMOSHI = 'qsnms'
STATE_MEIRIQIANDAOPOPUP = 'mrqdpp'
STATE_MEIRIQIANDAOPOPUP_OK = 'mrqdpp-ok'
STATE_LINGJINBI = 'jinbi'
STATE_AD_VIDEO = 'ad'
STATE_AD_VIDEO_AGAIN = 'ad-again'
STATE_SHUASHIPIN = 'shuashipin'
COLOR_TITLE_BAR_LINGJINBI = [113, 80, 255]
COLOR_TITLE_BAR_LINGJINBI_DARK = [128, 42, 51]


class DouYinDriver(appdriver.AppDriver):

    tagMain = ['关注.{0,6}', '推荐', '精选']
    tagLingJinBi = ['金币收益', '现金收益']
    taskItem = None
    idleTimeBegin = 0

    def __init__(self) -> None:
        self.phone = screen.SamSungNote4()
        self.imgName = 'screen.png'
        self.srcDir = '/sdcard/Pictures'
        self.dstDir = 'd:/cyc/douyin'
        self.appName = '抖音极速版'
        super().__init__()

    def isAtDesktop(self):
        tags = ['联系人', '信息', '浏览器', '应用程序']
        # 至少匹配3个
        cnt = self.getMatchCount(tags, self.matchTextItemAtBottom)
        if cnt >= 3:
            print("isAtDesktop -> YES")
            return True
        print("isAtDesktop -> NO")
        return False

    def onAtDesktop(self):
        cnt = self.onStateChanged(STATE_DESKTOP)
        if cnt > 1:
            txtItem = self.matchTextItem(self.appName)
            if txtItem != None:
                self.adb.clickPoint(txtItem.getClickXY())
                self.onStateChanged('none')

    def isAtMainPage(self):
        tags = {'首页', '朋友', '消息.{0,3}', '我.{0,3}'}
        # 至少匹配三个
        cnt = self.getMatchCount(tags, self.matchTextItemAtBottom)
        if cnt >= 3:
            print("isAtMainPage -> YES")
            return True
        print("isAtMainPage -> NO")
        return False

    def onMainPage(self):
        cnt = self.onStateChanged(STATE_MAIN)
        x = self.phone.width() / 2
        y = self.phone.getBottomBarY()
        print('onMainPage 点击钱包位置')
        self.adb.click(x, y)

    def isAtQingShaoNianMoShi(self):
        tags = {'青少年模式', '我知道了', '开启青少年.*'}
        # 至少匹配2个
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt >= 2:
            print("isAtQingShaoNianMoShi -> YES")
            return True
        print("isAtQingShaoNianMoShi -> NO")
        return False

    def onQingShaoNianMoShi(self):
        cnt = self.onStateChanged(STATE_QINGSHAONIANMOSHI)
        if cnt > 1:
            txtItem = self.matchTextItem('我知道了')
            if txtItem != None:
                print('onMainPage 点击 我知道了')
                self.adb.clickPoint(txtItem.getClickXY())
                return
        print('onMainPage error')

    def isAtLingJinBiPage(self):
        clr = self.getCurrentImageMajorColor(
            0, 0, self.phone.w, self.phone.getTitleBarY1Y2()[1])
        if clr.getColorDistance(COLOR_TITLE_BAR_LINGJINBI) < 10 or clr.getColorDistance(COLOR_TITLE_BAR_LINGJINBI_DARK) < 10:
            print('isAtLingJinBiPage -> YES')
            return True

        print('isAtLingJinBiPage -> NO')
        return False

    def onLingJinBi(self):
        cnt = self.onStateChanged(STATE_LINGJINBI)
        curtime = int(time.time())
        if cnt == 1:
            #刚刚回到这，啥也不干
            self.idleTimeBegin = curtime
            return
        diff = curtime - self.idleTimeBegin
        if diff > 5 * 60:
            #超过5分钟了，说明没找到任何任务，滚动下屏幕吧
            self.swipeUp()
        else:
            self.swipeDown()

    # 每日签到弹框
    def isAtMeiRiQianDaoPopup(self):
        tags = {'每日签到', '立即签到.*', '签到提醒', '签到可领'}
        # 至少匹配三个
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt >= 3:
            print("isAtMeiRiQianDaoPopup -> YES")
            return True
        print("isAtMeiRiQianDaoPopup -> NO")
        return False

    def onMeiRiQianDaoPopup(self):
        cnt = self.onStateChanged(STATE_MEIRIQIANDAOPOPUP)
        if cnt < 2:
            return

        txtItem = self.matchTextItem('立即签到.*')
        if txtItem != None:
            print("onMeiRiQianDaoPopup click 立即签到")
            self.adb.clickPoint(txtItem.getClickXY())
            return

    def isAtAdVideo(self):
        tags = {'广告', '反馈', '.*.*s后可领奖励'}
        # 至少匹配三个
        cnt = self.getMatchCount(tags, self.matchTextItemAtTop)
        if cnt == 3:
            print("isAtAdVideo -> YES")
            return True
        print("isAtAdVideo -> NO")
        return False

    # 等待广告视频播完
    def onAdVideo(self):
        self.onStateChanged(STATE_AD_VIDEO)
        time.sleep(15)

    # 继续看视频
    def isAtWatchAdVideoAgain(self):
        tags = [['签到成功.*', '看广告视频再赚.*', '已连续签到.*'],
                ['再看一个视频额外获得.*', '领取奖励', '坚持退出']]
        for it in tags:
            cnt = self.getMatchCount(it, self.matchTextItem)
            if cnt >= 3:
                print('IsAtWatchAdVideoAgain -> YES')
                return True

        print('IsAtWatchAdVideoAgain -> NO')
        return False

    # 继续看视频
    def onWatchAdVideoAgain(self):
        cnt = self.onStateChanged(STATE_AD_VIDEO_AGAIN)
        if cnt < 2:
            return

        tags = ['看广告视频再赚.*', '领取奖励']
        for it in tags:
            txtItem = self.matchTextItem(it)
            if txtItem != None:
                print('onWatchAdVideoAgain click ' + it)
                self.adb.clickPoint(txtItem.getClickXY())
                return

    def isTaskItemFound(self):
        tasks = {'看广告赚金币': '去领取'}
        for it in tasks:
            titles = self.matchAllTextItem(it)
            btns = self.matchAllTextItem(tasks[it])
            if titles == None or btns == None:
                print("isTaskItemFound -> NO")
                return False

            for t in titles:
                for b in btns:
                    if t.isHorizontalAlignWith(b):
                        self.taskItem = [it, b]
                        print("isTaskItemFound -> YES")
                        return True
        print("isTaskItemFound -> NO")
        return False

    def onTaskItemFount(self):
        cnt = self.onStateChanged(self.taskItem[0])
        if cnt > 1:
            self.adb.clickPoint(self.taskItem[1].getClickXY())

    def onShuaShiPin(self):
        cnt = self.onStateChanged(STATE_SHUASHIPIN)
        self.swipeUp()

    # 运行
    def runZhuanQianRenWu(self, timeout=30*60):
        timeBegin = time.time()
        cnt = 1
        upOrDown = 0
        while time.time() - timeBegin < timeout:
            print('\n================= runZhuanQianRenWu %d =================\n' % (cnt))
            cnt += 1
            time.sleep(15)
            ocrRes = self.makeScreenCapGetText()
            if self.isAtDesktop():
                self.onAtDesktop()
            elif self.isAtQingShaoNianMoShi():
                self.onQingShaoNianMoShi()
            elif self.isAtMainPage():
                self.onMainPage()
            elif self.isAtMeiRiQianDaoPopup():
                self.onMeiRiQianDaoPopup()
            elif self.isAtAdVideo():
                self.onAdVideo()
            elif self.isAtWatchAdVideoAgain():
                self.onWatchAdVideoAgain()
            elif self.isTaskItemFound():
                self.onTaskItemFount()
            elif not self.isAtLingJinBiPage():
                self.adb.goBack()
            else:
                pass

    def runShuaShiPin(self, timeout=30*60):
        timeBegin = time.time()
        cnt = 1
        upOrDown = 0
        while time.time() - timeBegin < timeout:
            print('\n================= runShuaShiPin %d =================\n' % (cnt))
            cnt += 1
            time.sleep(10)
            ocrRes = self.makeScreenCapGetText()
            if self.isAtDesktop():
                self.onAtDesktop()
            elif self.isAtQingShaoNianMoShi():
                self.onQingShaoNianMoShi()
            elif self.isAtMainPage():
                self.onShuaShiPin()
            else:
                self.adb.goBack()

    def run(self):
        while True:
            self.runShuaShiPin(10*60)
            self.runZhuanQianRenWu(10*60)

def main():
    douyin = DouYinDriver()
    argc = len(sys.argv)
    if argc > 1 and sys.argv[1].lower() == '-c':
        douyin.onLingJinBi()
    else:
        douyin.run()


if __name__ == '__main__':
    main()
