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
	
	def isHorizontalAlignWith(self, txtItem, diff=100):
		pt1 = self.getClickXY()
		pt2 = txtItem.getClickXY()
		return abs(pt1[1] - pt2[1]) < diff
		
	def isVerticalAlignWith(self, txtItem, diff=100):
		pt1 = self.getClickXY()
		pt2 = txtItem.getClickXY()
		return abs(pt1[0] - pt2[0]) < diff

	def isEqualTo(self, txtItem):
		if txtItem == None:
			return False
		return self.isHorizontalAlignWith(txtItem, 10) and self.isVerticalAlignWith(txtItem, 10)


