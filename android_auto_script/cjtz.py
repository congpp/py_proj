# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from adbdriver import *
from paddleocr import PaddleOCR, draw_ocr
import cvimage
import cv2

appName = '超级兔子数据'
ocr = PaddleOCR(use_angle_cls=False, lang="ch")
imgName='cjtz_screen.png'
srcImg = '/sdcard/Pictures/' + imgName
dstDir = 'H:/cjtz'
dstImg = dstDir + '/' + imgName

if not os.path.exists(dstDir):
	os.mkdir(dstDir)

def navigateToAboutUs():
	adb = AdbDriver()
	if True:
		adb.screenCap(srcImg)
		adb.pullFile(srcImg, dstImg)
		img = cvimage.Image(dstImg)
		t = 7.0/8.0
		h = 1.0 - t
		c = img.cropVerticalPercent(t, h)
		txt = ocr.ocr(c)
		#cv2.imwrite(dstDir + '/mine.png', c)
		#txt = ocr.ocr(dstDir + '/mine.png')
		print(txt)
		txtItem = findTextItem(txt, '我的')
		pt = txtItem.getClickPoint()
		adb.click(pt.x, pt.y + t * img.height())
	time.sleep(5)
	if True:
		adb.screenCap(srcImg)
		adb.pullFile(srcImg, dstImg)
		#txt = ocr.readtext(dstImg)
		img = cvimage.Image(dstImg)
		t = 1.0 / 4.0
		h = 2.0 / 4.0
		c = img.cropVerticalPercent(t, h)
		txt = ocr.ocr(c)
		#cv2.imwrite(dstDir + '/aboutus.png', c)
		#txt = ocr.ocr(dstDir + '/aboutus.png')
		txtItem = findTextItem(txt, '关于我们')
		pt = txtItem.getClickPoint()
		adb.click(pt.x, pt.y + t * img.height())

def main():
	try:
		navigateToAboutUs()
	except Exception as e:
		raise e

if __name__ == '__main__':
	main()
