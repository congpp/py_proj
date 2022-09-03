# -*- coding: UTF-8 -*-
import sys
import os
from shapely.geometry import *

class OcrTextItem:
	def __init__(self, item):
		self.poly = Polygon(item[0])
		self.text = item[1][0]
		self.confidentLevel = item[1][1]

	def getClickPoint(self):
		pts = list(self.poly.exterior.coords)
		la = LineString((pts[0], pts[2]))
		lb = LineString((pts[1], pts[3]))
		lc = la.intersection(lb)
		return Point(lc.bounds[0], lc.bounds[1])


def findTextItem(ocrRes, text):
	#[[[59.0, 56.0], [151.0, 56.0], [151.0, 81.0], [59.0, 81.0]], ('我的订单', 0.9951043725013733)]
	for t in ocrRes:
		if t[1][0] == text:
			print('ocr find: ' + t[1][0])
			return OcrTextItem(t)
		else:
			print('skip: ' + t[1][0])
	return None

def matchTextItem(ocrRes, text):
	#([[226, 170], [414, 170], [414, 220], [226, 220]], 'text', 0.8261902332305908),
	cmpl = re.compile(text)
	for t in ocrRes:
		if cmpl.match(t[1][0]) != None:
			print('ocr match: ' + t[1][0])
			return OcrTextItem(t)
	return None
