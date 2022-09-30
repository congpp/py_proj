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


class DouYinDriver(AppDriver):

    tagMain = ['关注.{0,6}', '推荐', '精选']
    tagLingJinBi = ['金币收益', '现金收益']
    taskItem = None

    def __init__(self) -> None:
        self.phone = screen.SamSungNote4()
        self.imgName = 'kuaishou.png'
        self.srcDir = '/sdcard/Pictures'
        self.dstDir = 'd:/cyc/kuaishou'
        self.appName = '快手'
        self.appid = 'com.smile.gifmaker'
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
        tags = ['首页', '精选', '消息.{0,3}', '我.{0,3}']
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
        txtItem = self.findTextItem('三')
        if txtItem != None:
            xy = txtItem.getClickXY()
            if xy[0] < self.phone.w * 0.2 and xy[1] < self.phone.h * 0.125:
                print('onMainPage 菜单按钮')
                self.adb.clickPoint(xy)
                return
        else:
            x = self.phone.w * 0.1
            y = self.phone.getTitleBarY()
            print('onMainPage 固定点击')
            self.adb.click(x, y)

    def isAtMainPageLeftPannel(self):
        tags = ['^扫一扫$', '^快手小店$', '^任务中心$', '^服务中心$',
                '^客服中心$', '^草稿箱$', '^历史记录$', '^时间管理$']
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt > 6:
            print("isAtMainPageLeftPannel -> YES")
            return True
        print("isAtMainPageLeftPannel -> NO")
        return False

    def onMainPageLeftPannel(self):
        cnt = self.onStateChanged(STATE_MAIN_LEFT_PANNEL)
        if cnt > 3:
            raise (AppError(STATE_MAIN_LEFT_PANNEL))
        elif cnt > 1:
            txtItem = self.matchTextItem('^任务中心$')
            if txtItem != None:
                self.adb.clickPoint(txtItem.getClickXY())

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
        if cnt > 5:
            raise (AppError(STATE_QINGSHAONIANMOSHI))
        if cnt > 1:
            txtItem = self.matchTextItem('我知道了')
            if txtItem != None:
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
        # 没找到任何任务，就滚动下屏幕
        if cnt > 20:
            raise (AppError(STATE_LINGJINBI))
        elif cnt in range(15, 20) or cnt in range(5, 10):
            self.swipeDown()
        elif cnt in range(1, 5) or cnt in range(10, 15):
            self.swipeUp()

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
        if cnt > 5:
            raise (AppError(STATE_MEIRIQIANDAOPOPUP))
        if cnt > 1:
            txtItem = self.matchTextItem('立即签到.*')
            if txtItem != None:
                print("onMeiRiQianDaoPopup click 立即签到")
                self.adb.clickPoint(txtItem.getClickXY())
                return

    def isAtKaiBaoXiang(self):
        tag = '^立即领\d+金币$'
        # 至少匹配三个
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

    def isAtAdVideo(self):
        tags = ['\d+s后可领取奖励']
        # 至少匹配三个
        cnt = self.getMatchCount(tags, self.matchTextItemAtTop)
        if cnt == len(tags) - 1:
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
        tasks = {'^看广告赚金币.+多看多得': '领福利'}
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

    def isAtGuangjieDeJiangLi(self):
        tags = ['逛逛街', '多赚钱', '浏览\\d+秒可领\\d+金币', '更多商品', '^\d+秒$']
        cnt = self.getMatchCount(tags, self.matchTextItem)
        if cnt == 3:
            print('isAtGuangjieDeJiangLi -> YES')
            return True

        print('isAtGuangjieDeJiangLi -> NO')
        return False

    def onGuangJieLingJinBi(self):
        cnt = self.onStateChanged('onGuangJieLingJinBi')
        if cnt > 20:
            raise (AppError('onZouLuZhuanJinBiBottom'))
        
        self.swipeUp()
        

    # 运行
    def runZhuanQianRenWu(self, timeout=30*60):
        timeBegin = time.time()
        while time.time() - timeBegin < timeout:
            try:
                print('\n================= runZhuanQianRenWu %d =================\n' % (
                    self.screencapId))
                time.sleep(10)
                self.makeScreenCapGetText()
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
                elif self.isAtKaiBaoXiang():
                    self.onKaiBaoXiang()
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
                print('\n================= runShuaShiPin %d =================\n' % (
                    self.screencapId))
                time.sleep(10)
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
        timeBegin = time.time()
        while time.time() - timeBegin < t:
            self.runZhuanQianRenWu(10*60)
            self.runShuaShiPin(10*60)


def main():
    douyin = DouYinDriver()
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
