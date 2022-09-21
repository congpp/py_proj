# -*- coding: UTF-8 -*-
from shapely.geometry import Point, Polygon, LineString

class OcrTextItem:
	poly = None
	text = ''
	confidentLevel = None

	def __init__(self, item):
		self.poly = Polygon(item[0])
		self.text = item[1][0]
		self.confidentLevel = item[1][1]

	def getClickXY(self):
		pts = list(self.poly.exterior.coords)
		la = LineString((pts[0], pts[2]))
		lb = LineString((pts[1], pts[3]))
		lc = la.intersection(lb)
		return lc.bounds[0], lc.bounds[1]

	def getLTRB(self):
		#LT RT RB LB
		pts = list(self.poly.exterior.coords)
		return pts[0][0], pts[0][1], pts[2][0], pts[2][1]

	def getClickPoint(self):
		return Point(self.getClickXY())
	
	def isHorizontalAlignWith(self, txtItem, diff=100):
		pt1 = self.getClickPoint()
		pt2 = txtItem.getClickPoint()
		return abs(pt1.y - pt2.y) < diff
		
	def isVerticalAlignWith(self, txtItem, diff=100):
		pt1 = self.getClickPoint()
		pt2 = txtItem.getClickPoint()
		return abs(pt1.x - pt2.x) < diff

