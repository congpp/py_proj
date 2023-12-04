# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from douyindriver import DouYin
from fanqiexiaoshuodriver import FanQieXiaoShuo
from kuaishoudriver import KuaiShou

def main():
	t = 6 * 60
	try:
		while(True):
			apps = [KuaiShou(), DouYin(), FanQieXiaoShuo(), ]
			for app in apps:
				app.goHome()
				app.run(t)
				app.goHome()
	except Exception as e:
		raise e

if __name__ == '__main__':
	main()
