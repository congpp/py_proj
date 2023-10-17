# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from adbdriver import *
from paddleocr import PaddleOCR
from appdriver import *
import screen
import cvimage
import cv2


STATE_DESKTOP = 'desktop'
STATE_LAUNCHING = 'launching'
STATE_MAIN = 'main'
STATE_QINGSHAONIANMOSHI = 'qsnms'
STATE_MEIRIQIANDAOPOPUP = 'mrqdpp'
STATE_MEIRIQIANDAOPOPUP_OK = 'mrqdpp-ok'
STATE_LINGJINBI = 'jinbi'
STATE_LINGJINBI_POPUP = 'jinbi-popup'
STATE_AD_VIDEO = 'ad'
STATE_AD_VIDEO_AGAIN = 'ad-again'
STATE_AD_GPS = 'gps'
STATE_SHUASHIPIN = 'shuashipin'
STATE_ERROR = 'error'
COLOR_TITLE_BAR_LINGJINBI = [255, 223, 235]
COLOR_TITLE_BAR_LINGJINBI_DARK = [0x33, 0x33, 0x33]


class FanQieXiaoShuo(AppDriver):

    taskItem = None

    def __init__(self) -> None:
        self.phone = screen.XiaoMiMix2()
        self.imgName = 'screen.png'
        self.srcDir = '/sdcard/Pictures'
        self.dstDir = 'd:/zhuanqian/fanqiexiaoshuo'
        self.appName = '番茄免费小说'
        self.appid = 'com.dragon.read'
        self.activity = 'com.dragon.read.pages.splash.SplashActivity'
        super().__init__()

    def isAtDesktop(self):
        tags = ['文件管理', '小爱音箱', '美颜相机', '相册']
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
            self.adb.startApp(self.appid, self.activity)

    def isAtMainPage(self):
        tags = {'书城', '分类', '福利', '我的'}
        cnt = self.getMatchCount(tags, self.matchTextItemAtBottom)
        if cnt >= 3:
            print("isAtMainPage -> YES")
            return True
        print("isAtMainPage -> NO")
        return False

    def onMainPage(self):
        cnt = self.onStateChanged(STATE_MAIN)
        if cnt > 3:
            raise (AppError(STATE_MAIN))
        x = self.phone.width() / 2
        y = self.phone.getBottomBarY()
        print('onMainPage 点击钱包位置')
        self.adb.click(x, y)

    def isAtQingShaoNianMoShi(self):
        tags = {'青少年模式', '我知道了', '开启青少年.*'}
        # 至少匹配2个
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt > 1:
            print("isAtQingShaoNianMoShi -> YES")
            return True
        print("isAtQingShaoNianMoShi -> NO")
        return False

    def onQingShaoNianMoShi(self):
        cnt = self.onStateChanged(STATE_QINGSHAONIANMOSHI)
        if cnt > 3:
            raise (AppError(STATE_QINGSHAONIANMOSHI))
        if cnt > 1:
            txtItem = self.matchTextItem('我知道了')
            if txtItem != None:
                print('onMainPage 点击 我知道了')
                self.adb.clickPoint(txtItem.getClickXY())
                return
        print('onMainPage error')

    def isAtLingJinBiPage(self):
        tags = {'福利中心', '福利商城'}
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt == 2:
            print('isAtLingJinBiPage -> YES')
            return True

        print('isAtLingJinBiPage -> NO')
        return False

    def onLingJinBi(self):
        cnt = self.onStateChanged(STATE_LINGJINBI)
        curtime = int(time.time())
        # 没找到任何任务，就滚动下屏幕
        if cnt >= 12:
            raise (AppError(STATE_LINGJINBI))
        elif cnt in range(3, 6) or cnt in range(9, 12):
            self.swipeDown()
        elif cnt in range(1, 3) or cnt in range(6, 9):
            self.swipeUp()

    def isAtLingJinBiPageWithPopup(self):
        tags = {'福利中心', '福利商城'}
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt == 2:
            clr = self.getCurrentImageMajorColor(
                0, 0, self.phone.w, self.phone.getTitleBarY1Y2()[1])
            if clr.getColorDistance(COLOR_TITLE_BAR_LINGJINBI_DARK) < 10:
                print('isAtLingJinBiPageWithPopup -> YES')
                return True

        print('isAtLingJinBiPageWithPopup -> NO')
        return False

    def onLingJinBiPageWithPopup(self):
        cnt = self.onStateChanged(STATE_LINGJINBI_POPUP)
        if cnt > 2:
            raise(AppError(STATE_LINGJINBI_POPUP))

    def isAtXinBanBenPopup(self):
        tags = {'新版本邀请你来抢先体验', '以后再说', '优先体验'}
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt == 3:
            print('isAtXinBanBenPopup -> YES')
            return True

        print('isAtXinBanBenPopup -> NO')
        return False

    def onXinBanBenPopup(self):
        cnt = self.onStateChanged('onXinBanBenPopup')
        if cnt > 3:
            raise (AppError('onXinBanBenPopup'))
        if cnt > 1:
            txtItem = self.matchTextItem('以后再说')
            if txtItem != None:
                print("onMeiRiQianDaoPopup click 以后再说")
                self.clickTextItemLeft(txtItem)


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
        if cnt > 3:
            raise (AppError(STATE_MEIRIQIANDAOPOPUP))
        if cnt > 1:
            txtItem = self.matchTextItem('立即签到.*')
            if txtItem != None:
                print("onMeiRiQianDaoPopup click 立即签到")
                self.clickTextItemLeft(txtItem)
                return

    def isAtKaiBaoXiang(self):
        tag = '开宝箱得金币'
        # 至少匹配三个
        txtItem = self.findTextItemEx(lambda txtItem: re.match(
            tag, txtItem.text) != None and txtItem.getClickXY() > (self.phone.w * 0.60, self.phone.h * 7/8))
        if txtItem != None:
            print("isAtKaiBaoXiang -> YES")
            self.taskItem = (tag, txtItem)
            return True
        print("isAtKaiBaoXiang -> NO")
        return False

    def onKaiBaoXiang(self):
        cnt = self.onStateChanged(self.taskItem[0])
        if cnt > 3:
            raise (AppError(STATE_MEIRIQIANDAOPOPUP))
        if cnt > 1:
            self.adb.clickPoint(self.taskItem[1].getClickXY())

    def isAtAdVideo(self):
        tags = {'^广告.*', '^%ds$', '.*s后可领奖励$'}
        cnt = self.getMatchCount(tags, self.matchTextItemAtTop)
        if cnt >= 2:
            print("isAtAdVideo -> YES")
            return True
        print("isAtAdVideo -> NO")
        return False

    # 等待广告视频播完
    def onAdVideo(self):
        cnt = self.onStateChanged(STATE_AD_VIDEO)
        if cnt > 3:
            raise (AppError(STATE_AD_VIDEO))
        time.sleep(15)

    def isAtGPSAuthorize(self):
        tags = {'^地理位置授权$', '^不允许$', '^允许$', '^允许http.*'}
        # 至少匹配三个
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt >= 3:
            print("isAtGPSAuthorize -> YES")
            return True
        print("isAtGPSAuthorize -> NO")
        return False
        
    def onGPSAuthorize(self):
        cnt = self.onStateChanged(STATE_AD_GPS)
        if cnt > 3:
            raise (AppError(STATE_AD_GPS))
        if cnt > 1:
            txtItem = self.matchTextItem('^不允许$')
            if txtItem != None:
                self.clickTextItemLeft(txtItem)

    # 继续看视频
    def isAtWatchAdVideoAgain(self):
        tags = [[r'签到成功.*', r'看视频最高.*', r'已连续签到.*'],
                [r'签到专属福利', r'^.\d+金$', r'看视频最高.*'],
                [r'恭喜你.*', r'^.\d+金币$', r'看视频最高.*'],
                [r'恭喜你.*', r'\+\d+', r'看视频最高.*'],
                [r'再看.*额外获得.*', '领取奖励', '坚持退出'],
                [r'再看.*奖励', '继续观看', '坚持退出'],
                [r'本轮金币已领取', '看视频最高.*'],
                [r'看一个视频.*加倍', '去加倍.*'],
                ]
        for it in tags:
            cnt = self.getMatchCount(it, self.matchTextItem)
            if cnt == len(it):
                print('IsAtWatchAdVideoAgain -> YES')
                return True

        print('IsAtWatchAdVideoAgain -> NO')
        return False

    # 继续看视频
    def onWatchAdVideoAgain(self):
        cnt = self.onStateChanged(STATE_AD_VIDEO_AGAIN)
        if cnt > 3:
            raise (AppError(STATE_AD_VIDEO_AGAIN))
        if cnt > 1:
            tags = ['^看视频最高.*', '^领取奖励$', '^继续观看$']
            for it in tags:
                txtItem = self.matchTextItem(it)
                if txtItem != None:
                    print('onWatchAdVideoAgain click ' + it)
                    self.clickTextItemLeft(txtItem)
                    return

    def isTaskItemFound(self):
        tasks = {'看视频赚金币': '立即领取$',
                '已连续签到.*签到可得.*金币$' : '^签到$',
                '签到专属福利' : '^去领取$'}
        for it in tasks:
            titles = self.matchAllTextItem(it)
            btns = self.matchAllTextItem(tasks[it])
            if titles == None or btns == None:
                print("isTaskItemFound -> NO")
                return False

            for t in titles:
                for b in btns:
                    if b.getClickXY()[0] > self.phone.w * 0.6 and t.isHorizontalAlignWith(b) and not t.isEqualTo(b):
                        self.taskItem = [it, b]
                        print("isTaskItemFound -> YES")
                        return True
        print("isTaskItemFound -> NO")
        return False

    def onTaskItemFount(self):
        cnt = self.onStateChanged(self.taskItem[0])
        if cnt > 3:
            raise (AppError(self.taskItem[0]))
        if cnt > 1:
            self.adb.clickPoint(self.taskItem[1].getClickXY())

    def onShuaShiPin(self):
        if self.isScreenTextNotChanged():
            cnt = self.onStateChanged(STATE_SHUASHIPIN)
            if cnt > 3:
                raise (AppError(STATE_SHUASHIPIN))
        self.swipeUp()

    def onError(self):
        cnt = self.onStateChanged(STATE_ERROR)
        if cnt > 3:
            raise (AppError(STATE_ERROR))
        self.adb.goBack()

    # 运行
    def runZhuanQianRenWu(self, timeout=30*60):
        timeBegin = time.time()
        while time.time() - timeBegin < timeout:
            try:
                print(f'\n==== {self.appName} runZhuanQianRenWu {self.screencapId} ====\n')
                time.sleep(5)
                self.makeScreenCapGetText()
                if self.isAtDesktop():
                    self.onAtDesktop()
                elif self.isAtXinBanBenPopup():
                    self.onXinBanBenPopup()
                elif self.isAtQingShaoNianMoShi():
                    self.onQingShaoNianMoShi()
                elif self.isAtMeiRiQianDaoPopup():
                    self.onMeiRiQianDaoPopup()
                elif self.isAtWatchAdVideoAgain():
                    self.onWatchAdVideoAgain()
                elif self.isAtAdVideo():
                    self.onAdVideo()
                elif self.isAtKaiBaoXiang():
                    self.onKaiBaoXiang()
                # elif self.isAtZouLuZhuanJinBiTop(): self.onZouLuZhuanJinBiTop()
                # elif self.isAtZouLuZhuanJinBiBottom: self.onZouLuZhuanJinBiBottom()
                elif self.isTaskItemFound():
                    self.onTaskItemFount()
                elif self.isAtLingJinBiPage():
                    self.onLingJinBi()
                elif self.isAtMainPage():
                    self.onMainPage()
                else:
                    self.onError()
            except AppError as e:
                print(e)
                self.goHome()

    def run(self, t):
        timeBegin = time.time()
        while time.time() - timeBegin < t:
            self.runZhuanQianRenWu(10*60)


def main():
    douyin = FanQieXiaoShuo()
    debug = True
    argc, t = len(sys.argv), 30 * 60
    for it in range(1, argc):
        s = sys.argv[it].lower()
        if s == '-t':
            t = int(sys.argv[it+1])

    douyin.debug = debug
    douyin.run(t)
        
    douyin.goHome()
    print(sys.argv[0] + " exit");


if __name__ == '__main__':
    main()
