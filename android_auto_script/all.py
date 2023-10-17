# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
import douyindriver
import fanqiexiaoshuodriver

def main():
	t = 20 * 60
	try:
		while(True):
			apps = [douyindriver.DouYin(), fanqiexiaoshuodriver.FanQieXiaoShuo()]
			for app in apps:
				app.goHome()
				app.run(t)
				app.goHome()
	except Exception as e:
		raise e

if __name__ == '__main__':
	main()
