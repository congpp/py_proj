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
STATE_MAIN = 'main'
STATE_MAIN_LEFT_PANNEL = 'main-left-pannel'
STATE_QINGSHAONIANMOSHI = 'qsnms'

STATE_MEIRIQIANDAOPOPUP = 'mrqdpp'
STATE_MEIRIQIANDAOPOPUP_OK = 'mrqdpp-ok'
STATE_LINGJINBI = 'jinbi'
STATE_AD_VIDEO = 'ad'
STATE_AD_VIDEO_AGAIN = 'ad-again'
STATE_SHUASHIPIN = 'shuashipin'
STATE_ERROR = 'error'
COLOR_TITLE_BAR_LINGJINBI = [78, 48, 253]
COLOR_TITLE_BAR_LINGJINBI_DARK = [33, 38, 99]


class KuaiShou(AppDriver):

    tagMain = ['关注.{0,6}', '推荐', '精选']
    tagLingJinBi = ['金币收益', '现金收益']
    taskItem = None

    def __init__(self) -> None:
        self.phone = screen.XiaoMiMix2()
        self.imgName = 'screen.png'
        self.srcDir = '/sdcard/Pictures'
        self.dstDir = 'd:/zhuanqian/kuaishou'
        self.appName = '快手'
        self.appid = 'com.kuaishou.nebula'
        self.activity = 'com.yxcorp.gifshow.HomeActivity'
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
        tags = ['首页', '朋友', '^去赚钱.*', '^我.*']
        # 至少匹配三个
        cnt = self.getMatchCount(tags, self.matchTextItemAtBottom)
        if cnt >= 3:
            print("isAtMainPage -> YES")
            return True
        print("isAtMainPage -> NO")
        return False

    def onMainPage(self):
        cnt = self.onStateChanged(STATE_MAIN)
        if cnt > 5:
            raise (AppError(STATE_MEIRIQIANDAOPOPUP))
        txtItem = self.findTextItem('去赚钱')
        if txtItem != None:
            self.adb.clickPoint(txtItem.getClickXY())
        else:
            x = self.phone.w * 0.1
            y = self.phone.getTitleBarY()
            print('onMainPage 固定点击')
            self.adb.click(x, y)

    def isAtMainPageLeftPannel(self):
        tags = ['^扫一扫$', '^快手小店$', '^朋友在看$', '^私信$',
                '^服务中心$', '^草稿箱$', '^历史记录$', '^官方客服$']
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt >= 6:
            print("isAtMainPageLeftPannel -> YES")
            return True
        print("isAtMainPageLeftPannel -> NO")
        return False

    def onMainPageLeftPannel(self):
        cnt = self.onStateChanged(STATE_MAIN_LEFT_PANNEL)
        if cnt > 3:
            raise (AppError(STATE_MAIN_LEFT_PANNEL))
        elif cnt > 1:
            txtItem = self.matchTextItem('^去赚钱$')
            if txtItem != None:
                self.adb.clickPoint(txtItem.getClickXY())

    def isAtQingShaoNianMoShi(self):
        tags = {'^青少年模式', '我知道了', '^开启青少年.*'}
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt >= 2:
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
                self.adb.clickPoint(txtItem.getClickXY())
                return
        print('onMainPage error')

    def isAtLingJinBiPage(self):
        tags = {'^任务中心$', '.*限时奖励$', '我的金币', '我的抵用金'}
        cnt = self.getMatchCount(tags, self.matchTextItemAtTop)
        if cnt >= 2:
            print('isAtLingJinBiPage -> YES')
            return True

        print('isAtLingJinBiPage -> NO')
        return False

    def onLingJinBi(self):
        cnt = self.onStateChanged(STATE_LINGJINBI)
        # 没找到任何任务，就滚动下屏幕
        if cnt >= 12:
            raise (AppError(STATE_LINGJINBI))
        elif 3 <= cnt < 6 or 9 <= cnt < 12:
            self.swipeDown()
        elif 1 <= cnt < 3 or 6 <= cnt < 9:
            self.swipeUp()

    # 每日签到弹框
    def isMeiRiQianDaoBtnFound(self):
        tag = '^立即签到$'
        # 至少匹配三个
        txtItem = self.findTextItem(tag)
        if txtItem:
            self.taskItem = [tag, txtItem]
            print("isMeiRiQianDaoBtnFound -> YES")
            return True
        print("isMeiRiQianDaoBtnFound -> NO")
        return False

    def onMeiRiQianDao(self):
        cnt = self.onStateChanged(STATE_MEIRIQIANDAOPOPUP)
        if cnt > 3:
            raise (AppError(STATE_MEIRIQIANDAOPOPUP))
        if cnt > 1:
            self.adb.clickPoint(self.taskItem[1].getClickXY())
            return

    def isAtKaiBaoXiang(self):
        tag = '^开宝箱得金币$'
        txtItem = self.findTextItemEx(lambda txtItem: re.match(
            tag, txtItem.text) != None and txtItem.getClickXY() > (self.phone.w * 3 / 4, self.phone.h * 7/8))
        if txtItem != None:
            print("isAtKaiBaoXiang -> YES")
            self.taskItem = (tag, txtItem)
            return True
        print("isAtKaiBaoXiang -> NO")
        return False

    def onKaiBaoXiang(self):
        cnt = self.onStateChanged(self.taskItem[0])
        if cnt > 5:
            raise (AppError(STATE_MEIRIQIANDAOPOPUP))
        if cnt > 1:
            self.adb.clickPoint(self.taskItem[1].getClickXY())

    def isAtKaiBaoXiangPopup(self):
        tags={'恭喜你获得', '.*金币', '看内容最高可得.*', '赚更多'}
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt == 3:
            print('isAtKaiBaoXiangPopup -> YES')
            return True
        print('isAtKaiBaoXiangPopup -> NO')
        return False

    def onKaiBaoXiangPopup(self):
        cnt = self.onStateChanged('onKaiBaoXiangPopup')
        if cnt > 2:
            raise AppError('onKaiBaoXiangPopup')
        txtItem = self.matchTextItem('看内容最高可得.*')
        if txtItem:
            self.adb.clickPoint(txtItem.getClickXY())


    def isAtAdVideo(self):
        tag = '^\d+s后可领取奖励$'
        txtItem = self.findTextItemEx(lambda txtItem: re.match(
            tag, txtItem.text) != None and txtItem.getClickXY()[1] < self.phone.h * 0.2)
        if txtItem != None:
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

    def isAtZhiBoJian(self):
        tags = {'^更多直播$', '.*\d\d.\d\d$', '^今日爆款$', '^去开卡$'}
        cnt = self.getMatchCount(tags, self.matchTextItemAtRight)
        if cnt >= 2:
            print("isAtZhiBoJian -> YES")
            return True
        print("isAtZhiBoJian -> NO")
        return False

    def onAdZhiBoJian(self):
        cnt = self.onStateChanged('onAdZhiBoJian')
        if cnt > 3:
            raise (AppError('onAdZhiBoJian'))
        time.sleep(20)

    # 继续看视频
    def isAtWatchAdVideoAgain(self):
        tags = [['恭喜你已获得奖励', '继续观看视频最高得\d=金币$', '再看一个', '坚持退出'],
                ['^开宝箱奖励$', '^.+后可继续开启宝箱$', '看精彩视频再赚\d+金币']
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
        if cnt > 5:
            raise (AppError(STATE_AD_VIDEO))
        if cnt > 1:
            tags = ['^再看一个$', '看精彩视频再赚\d+金币']
            for it in tags:
                txtItem = self.matchTextItem(it)
                if txtItem != None:
                    print('onWatchAdVideoAgain click ' + it)
                    self.adb.clickPoint(txtItem.getClickXY())
                    return

    def isTaskItemFound(self):
        tasks = {'^看广告得.*金币.*': '^领福利$',
                '看激励广告.*':'^去观看$'}
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
        if cnt > 5:
            raise (AppError(self.taskItem[0]))
        if cnt > 1:
            self.adb.clickPoint(self.taskItem[1].getClickXY())

    def onShuaShiPin(self):
        if self.isScreenTextNotChanged():
            cnt = self.onStateChanged(STATE_SHUASHIPIN)
            if cnt > 5:
                raise (AppError(STATE_SHUASHIPIN))
        self.swipeUp()

    def onError(self):
        cnt = self.onStateChanged(STATE_ERROR)
        if cnt > 5:
            raise (AppError(STATE_ERROR))

        self.adb.goBack()

    # 运行

    def runZhuanQianRenWu(self, timeout=30*60):
        timeBegin = time.time()
        while time.time() - timeBegin < timeout:
            try:
                print(f'\n==== {self.appName} runZhuanQianRenWu {self.screencapId} =================\n')
                time.sleep(10)
                self.makeScreenCapGetText()
                if self.isAtDesktop():
                    self.onAtDesktop()
                elif self.isAtQingShaoNianMoShi():
                    self.onQingShaoNianMoShi()
                elif self.isAtMainPage():
                    self.onMainPage()
                elif self.isAtMainPageLeftPannel():
                    self.onMainPageLeftPannel()
                elif self.isMeiRiQianDaoBtnFound():
                    self.onMeiRiQianDao()
                elif self.isAtAdVideo():
                    self.onAdVideo()
                elif self.isAtWatchAdVideoAgain():
                    self.onWatchAdVideoAgain()
                elif self.isAtKaiBaoXiang():
                    self.onKaiBaoXiang()
                elif self.isAtKaiBaoXiangPopup():
                    self.onKaiBaoXiangPopup()
                elif self.isAtZhiBoJian():
                    self.onZhiBoJian()
                # elif self.isAtZouLuZhuanJinBiTop(): self.onZouLuZhuanJinBiTop()
                # elif self.isAtZouLuZhuanJinBiBottom: self.onZouLuZhuanJinBiBottom()
                elif self.isTaskItemFound():
                    self.onTaskItemFount()
                elif self.isAtLingJinBiPage():
                    self.onLingJinBi()
                else:
                    self.onError()
            except AppError as e:
                print(e)
                self.goHome()

    def runShuaShiPin(self, timeout=30*60):
        timeBegin = time.time()
        while time.time() - timeBegin < timeout:
            try:
                print(f'\n==== {self.appName} runShuaShiPin {self.screencapId} =================\n')
                time.sleep(5)
                self.makeScreenCapGetText()
                if self.isAtDesktop():
                    self.onAtDesktop()
                elif self.isAtQingShaoNianMoShi():
                    self.onQingShaoNianMoShi()
                elif self.isAtMainPage():
                    self.onShuaShiPin()
                else:
                    self.onError()
            except AppError as e:
                print(e)
                self.goHome()

    def run(self, t):
        self.runZhuanQianRenWu(t/2)
        self.goHome()
        self.runShuaShiPin(t/2)


def main():
    douyin = KuaiShou()
    ljb, ssp, debug = False, False, True
    argc, t = len(sys.argv), 30 * 60
    for it in range(1, argc):
        s = sys.argv[it].lower()
        if s == '-ljb':
            ljb = True
        elif s == '-ssp':
            ssp = True
        elif s == '-t':
            t = int(sys.argv[it+1])

    douyin.debug = debug
    if ljb:
        douyin.runZhuanQianRenWu(t)
    elif ssp:
        douyin.runShuaShiPin(t)
    else:
        douyin.run(t)

    douyin.goHome()


if __name__ == '__main__':
    main()
