# -*- coding: UTF-8 -*-
import cv2
import math


class Color:
    def __init__(self, rgb=[0, 0, 0]) -> None:
        self.rgb = rgb

    def toInt(self):
        return (self.rgb[2] << 16) | (self.rgb[1] << 8) | (self.rgb[0])

    def getColorDistance(self, rgb):
        r1, g1, b1 = self.rgb
        r2, g2, b2 = rgb
        rmean = (r1 + r2) / 2
        R = r1 - r2
        G = g1 - g2
        B = b1 - b2
        return math.sqrt((2+rmean/256)*(R**2)+4*(G**2)+(2+(255-rmean)/256)*(B**2))

class Image:
    def __init__(self, imgPath):
        self.img = cv2.imread(imgPath)

    def width(self):
        return len(self.img[0])

    def height(self):
        return len(self.img)

    def crop(self, l, t, w, h):
        print('crop: %d %d %d %d' % (l, t, w, h))
        return self.img[int(t):int(t+h), int(l):int(l+w)]

    def cropVertical(self, t, h):
        return self.crop(0, t, self.width(), h)

    def cropVerticalPercent(self, t, h):
        t = t*self.height()
        h = h*self.height()
        return self.crop(0, t, self.width(), h)

    def cropHorizontal(self, l, w):
        return self.crop(l, 0, w, self.height())

    def cropHorizontalPercent(self, l, w):
        l = l*self.width()
        w = w*self.width()
        return self.crop(l, 0, w, self.height())

    def getMajorColor(self, l, t, w, h):
        r = min(l+w, self.width())
        b = min(t+h, self.height())
        majorClr = 0
        majorCnt = 0
        clrMap = {}
        for y in range(t, b):
            for x in range(l, r):
                c = Color(self.img[y, x]).toInt()
                v = 0
                if c in clrMap:
                    v = clrMap[c]
                clrMap[c] = v+1
                if v+1 > majorCnt:
                    majorClr = self.img[y, x]
                    majorCnt = v+1
        print('major color: %s, repeats %d' % (majorClr, majorCnt))
        return Color(majorClr)

