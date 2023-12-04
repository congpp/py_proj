# -*- coding: UTF-8 -*-
import re
import sys
import os
import time
from ocrwrapper import *

"""
命令格式
adb shell input keyevent

//在屏幕上做划屏操作，前四个数为坐标点，后面是滑动的时间（单位毫秒）
adb shell input swipe 50 250 250 250 500

//在 100 100 位置长按 1000毫秒
adb shell input swipe 100 100 100 100 1000

//在屏幕上点击坐标点x=50 y=250的位置。
adb shell input tap 50 250

//输入字符abc
adb shell input text abc

附 其它按键值：
KEYCODE_HOME                按键Home
KEYCODE_BACK                返回键
KEYCODE_CALL                拨号键
KEYCODE_ENDCALL             挂机键
KEYCODE_0                   按键 0 
KEYCODE_1                   按键 1 
KEYCODE_2                   按键 2 
KEYCODE_3                   按键 3 
KEYCODE_4                   按键 4 
KEYCODE_5                   按键 5 
KEYCODE_6                   按键 6 
KEYCODE_7                   按键 7 
KEYCODE_8                   按键 8 
KEYCODE_9                   按键 9 
KEYCODE_DPAD_UP             导航键 向上
KEYCODE_DPAD_DOWN           导航键 向下
KEYCODE_DPAD_LEFT           导航键 向左
KEYCODE_DPAD_RIGHT          导航键 向右
KEYCODE_DPAD_CENTER         导航键 确定键
KEYCODE_VOLUME_UP           音量增加键
KEYCODE_VOLUME_DOWN         音量减小键
KEYCODE_POWER               电源键
KEYCODE_CAMERA              拍照键
KEYCODE_A                   按键 A 
KEYCODE_B                   按键 B 
KEYCODE_C                   按键 C 
KEYCODE_D                   按键 D 
KEYCODE_E                   按键 E 
KEYCODE_F                   按键 F 
KEYCODE_G                   按键 G 
KEYCODE_H                   按键 H 
KEYCODE_I                   按键 I 
KEYCODE_J                   按键 J 
KEYCODE_K                   按键 K 
KEYCODE_L                   按键 L 
KEYCODE_M                   按键 M 
KEYCODE_N                   按键 N 
KEYCODE_O                   按键 O 
KEYCODE_P                   按键 P 
KEYCODE_Q                   按键 Q 
KEYCODE_R                   按键 R 
KEYCODE_S                   按键 S 
KEYCODE_T                   按键 T 
KEYCODE_U                   按键 U 
KEYCODE_V                   按键 V 
KEYCODE_W                   按键 W 
KEYCODE_X                   按键 X 
KEYCODE_Y                   按键 Y 
KEYCODE_Z                   按键 Z 
KEYCODE_TAB                 Tab键
KEYCODE_ENTER               回车键
KEYCODE_DEL                 退格键
KEYCODE_FOCUS               拍照对焦键
KEYCODE_MENU                菜单键
KEYCODE_NOTIFICATION        通知键
KEYCODE_SEARCH              搜索键
KEYCODE_MUTE                话筒静音键
KEYCODE_PAGE_UP             向上翻页键
KEYCODE_PAGE_DOWN           向下翻页键
KEYCODE_ESCAPE              ESC键
KEYCODE_FORWARD_DEL         删除键
KEYCODE_CAPS_LOCK           大写锁定键
KEYCODE_SCROLL_LOCK         滚动锁定键
KEYCODE_BREAK               Break/Pause键
KEYCODE_MOVE_HOME           光标移动到开始键
KEYCODE_MOVE_END            光标移动到末尾键
KEYCODE_INSERT              插入键
KEYCODE_NUM_LOCK            小键盘锁
KEYCODE_VOLUME_MUTE         扬声器静音键
KEYCODE_ZOOM_IN             放大键
KEYCODE_ZOOM_OUT            缩小键
KEYCODE_PLUS                按键 + 
KEYCODE_MINUS               按键 - 
KEYCODE_STAR                按键 * 
KEYCODE_SLASH               按键 / 
KEYCODE_EQUALS              按键 = 
KEYCODE_AT                  按键 @ 
KEYCODE_POUND               按键 # 
KEYCODE_APOSTROPHE          按键    (单引号)
KEYCODE_BACKSLASH           按键  
KEYCODE_COMMA               按键 , 
KEYCODE_PERIOD              按键 . 
KEYCODE_LEFT_BRACKET        按键 [ 
KEYCODE_RIGHT_BRACKET       按键 ] 
KEYCODE_SEMICOLON           按键 ; 
KEYCODE_GRAVE               按键 ` 
KEYCODE_SPACE               空格键
KEYCODE_NUMPAD_0            小键盘按键 0 
KEYCODE_NUMPAD_1            小键盘按键 1 
KEYCODE_NUMPAD_2            小键盘按键 2 
KEYCODE_NUMPAD_3            小键盘按键 3 
KEYCODE_NUMPAD_4            小键盘按键 4 
KEYCODE_NUMPAD_5            小键盘按键 5 
KEYCODE_NUMPAD_6            小键盘按键 6 
KEYCODE_NUMPAD_7            小键盘按键 7 
KEYCODE_NUMPAD_8            小键盘按键 8 
KEYCODE_NUMPAD_9            小键盘按键 9 
KEYCODE_NUMPAD_ADD          小键盘按键 + 
KEYCODE_NUMPAD_SUBTRACT     小键盘按键 - 
KEYCODE_NUMPAD_MULTIPLY     小键盘按键 * 
KEYCODE_NUMPAD_DIVIDE       小键盘按键 / 
KEYCODE_NUMPAD_EQUALS       小键盘按键 = 
KEYCODE_NUMPAD_COMMA        小键盘按键 , 
KEYCODE_NUMPAD_DOT          小键盘按键 . 
KEYCODE_NUMPAD_LEFT_PAREN   小键盘按键 ( 
KEYCODE_NUMPAD_RIGHT_PAREN  小键盘按键 ) 
KEYCODE_NUMPAD_ENTER        小键盘按键回车

"""

class AdbDriver:
    class AdbError(Exception) : pass
    
    deviceName = ''

    """docstring for adb"""
    def __init__(self, deviceName=''):
        self.deviceName = deviceName

    #执行adb命令
    def runCmd(self, arg):
        cmd = ''
        if len(self.deviceName) > 0:
            cmd = 'adb -s ' + self.deviceName + ' ' + arg
        else:
            cmd = 'adb ' + arg
        print('adb run: ' + cmd)
        p = os.popen(cmd)
        text = p.read()
        p.close()
        if len(text) > 0:
            print('run res: ' + text)
        return text

    def devices(self):
        devices = self.runCmd('devices').replace('\t', ' ')
        ret=[]
        for l in devices.split('\n'):
            while '  ' in l: l = l.replace('  ', ' ')
            dev = l.split(' ', 1)
            if len(dev) == 2: ret.append(dev)
        return ret

    #删除手机文件 filePath
    def delFile(self, filePath):
        #adb -s 127.0.0.1:21503 shell rm -f weather.txt
        self.runCmd('shell rm -f "' + filePath + '"')
        return self.isFileExists(filePath) == False

    #手机文件 filePath 是否存在
    def isFileExists(self, filePath):
        #adb -s 127.0.0.1:21503 shell if [[ -e /root ]]; then echo yes; fi
        res = self.runCmd('shell if [[ -e "' + filePath + '" ]]; then echo yes; fi')
        return res.strip(' \t\r\n') == 'yes'

    #拉文件 srcPath 回来，保存到电脑 dstPath
    def pullFile(self, srcPath, dstPath):
        if len(dstPath) < 3:
            raise self.AdbError('pull file: dstPath must be a sub-dir, like "c:\\123"')
        #del
        if os.path.exists(dstPath):
            os.remove(dstPath)
        #adb -s 127.0.0.1:21503 pull srcPath dstPath
        self.runCmd('pull "%s" "%s"' % (srcPath, dstPath))
        return os.path.exists(dstPath)

    #截图，保存在手机 imgPath
    def screenCap(self, imgPath):
        #adb -s 127.0.0.1:21503 shell screencap imgPath
        self.runCmd('shell screencap ' + imgPath)
        return self.isFileExists(imgPath)

    #截图，保存在本地磁盘 imgPath，老机型不支持，老实用screenCap然后再pullFile回来
    def screenPull(self, imgPath):
        #adb -s 127.0.0.1:21503 shell screencap imgPath
        self.runCmd('exec-out screencap -p > %s' % (imgPath))
        return self.isFileExists(imgPath)

    def click(self, x, y):
        #adb shell input tap 50 250
        self.runCmd('shell input tap %d %d' % (x, y))

    def clickPoint(self, xy):
        #adb shell input tap 50 250
        self.runCmd('shell input tap %d %d' % (xy[0], xy[1]))

    def longPress(self, x1, y1, x2, y2, ms=1000):
        #adb shell input swipe 100 100 100 100 1000
        self.runCmd('shell input swipe %d %d %d %d %d' % (x1, y1, x2, y2, ms))

    def swipe(self, x1, y1, x2, y2, ms=1000):
        #adb shell input swipe 100 100 100 100 1000
        return self.longPress(x1, y1, x2, y2, ms)

    def input(self, text):
        #adb shell input tap 50 250
        self.runCmd('shell input text ' + text)
    
    def keyevent(self, event):
        #adb shell input keyevent
        self.runCmd('shell input keyevent ' + event)

    def goHome(self):
        self.keyevent('KEYCODE_HOME')
    
    def goBackN(self, n):
        if n == 0:
            return
        cmd = 'shell for i in `seq 0 %d`; do input keyevent KEYCODE_BACK; sleep 0.2; done' % (n - 1)
        self.runCmd(cmd)
        #for i in range(0, n):
        #    self.goBack()
        #    time.sleep(0.2)

    def goBack(self):
        self.keyevent('KEYCODE_BACK')

    def forceStop(self, appid):
        self.runCmd('shell am force-stop ' + appid)

    def volumnUp(self):
        self.keyevent('KEYCODE_VOLUME_UP')

    def volumnDown(self):
        self.keyevent('KEYCODE_VOLUME_DOWN')

    def volumnMute(self):
        self.keyevent('KEYCODE_VOLUME_MUTE')

    def getScreenSize(self):
        #adb shell wm size
        #Physical size: 1080x2160
        ret = self.runCmd('shell wm size')
        try:
            r = re.search(r'(\d+)x(\d+)', ret)
            if r != None:
                return (int(r[1]), int(r[2]))
        except Exception as e:
            print(e)
        return (0,0)
    
    def startApp(self, package, activity):
        ret = self.runCmd(f'shell am start {package}/{activity}')
        if (ret.find('Error:') >= 0):
            print('run app error')
            return False
        return True

    def dumpScreenXML(self, tempName):
        #adb shell /system/bin/uiautomator dump --compressed /sdcard/uidump.xml
        if self.isFileExists(tempName):
            self.delFile(tempName)
            
        ret = self.runCmd(f'shell /system/bin/uiautomator dump --compressed {tempName}')
        if (ret.find('UI hierchary dumped to:') >= 0):
            return True
        print('dump xml error')
        return True

    def pullScreenXML(self, srcPath, dstPath):
        if self.dumpScreenXML(srcPath):
            return self.pullFile(srcPath, dstPath)
        print('pull xml error')
        return False


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == '-devices':
        print(AdbDriver().devices())
    elif cmd == '-screencap':
        AdbDriver().screenCap('/sdcard/pictures/adb-driver-sc-%d.jpg' % (time.time()))