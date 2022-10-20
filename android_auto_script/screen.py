# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from xml.etree.ElementPath import findtext


class Screen():
    #@nbh notification bar height
    #@tbh title bar height
    def __init__(self, w, h, nbh, tbh) -> None:
        self.w = w
        self.h = h
        self.nbh = nbh
        self.tbh = tbh

    def width(self):
        return self.w
    
    def height(self):
        return self.h
    
    def getPercentX(self, x):
        return float(x) / self.w
        
    def getPercentY(self, y):
        return float(y) / self.h

    def getPercentPt(self, x, y):
        return self.getPercentX(x), self.getPercentY(y)
    
    def isPtBelowPercentOf(self, x, y, px1, py1):
        px, py = self.getPercentPt(x, y)
        return px <= px1 and py <= py1
        
    def isPtAbovePercentOf(self, x, y, px1, py1):
        px, py = self.getPercentPt(x, y)
        return px >= px1 and py >= py1
    
    def isPtWithinPercentOf(self, x, y, px1, py1, px2, py2):
        px, py = self.getPercentPt(x, y)
        return px1 <= px and px <= px2 and py1 <= py and py <= py2

    def isPtAtLeft(self, x, px1 = 0.3333):
        return self.getPercentX(x) < px1

    def isPtAtRight(self, x, px1 = 0.6666):
        return self.getPercentX(x) > px1

    def isPtAtTop(self, y, py = 0.3333):
        return self.getPercentY(y) < py

    def isPtAtBottom(self, y, py = 0.6666):
        return self.getPercentY(y) > py
        
    def isPtAtMiddleX(self, x, px1 = 0.3333, px2 = 0.6666):
        px = self.getPercentX(x)
        return px > px1 and px < px2
    
    def isPtAtMiddleY(self, y, py1 = 0.3333, py2 = 0.6666):
        py = self.getPercentY(y)
        return py > py1 and py < py2

    def getNotificationBarY1Y2(self):
        return 0, self.nbh

    def getNotificationBarY(self):
        return self.nbh + self.nbh / 2
        
    def getTitleBarY1Y2(self):
        return self.nbh, self.nbh + self.tbh

    def getTitleBarY(self):
        return self.nbh + self.tbh / 2

    def getBottomBarY1Y2(self, py = 19.0 / 20.0):
        return self.h * py, self.h

    def getBottomBarY(self, py = 19.0 / 20.0):
        t = self.h * py
        return t + (self.h - t) / 2


class SamSungNote4(Screen):
    def __init__(self) -> None:
        super().__init__(1440, 2560, 95, 200)

class XiaoMiMix2(Screen):
    def __init__(self) -> None:
        super().__init__(1080, 2160, 80, 126)