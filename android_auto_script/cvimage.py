# -*- coding: UTF-8 -*-
import cv2

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
