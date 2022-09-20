# -*- coding: UTF-8 -*-
import sys
import os
import re
import time
from adbdriver import *
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image

def main():
    try:
        img = sys.argv[1]
        ocr = PaddleOCR(use_angle_cls=False, lang="ch")
        txt = ocr.ocr(img)
        print(txt)

        image = Image.open(img).convert('RGB')
        boxes = [line[0] for line in txt]
        txts = [line[1][0] for line in txt]
        scores = [line[1][1] for line in txt]
        im_show = draw_ocr(image, boxes, txts, scores)#, font_path='/path/to/PaddleOCR/doc/simfang.ttf'
        im_show = Image.fromarray(im_show)
        im_show.save(img + '_ocr_res.jpg')
        os.system(img + '_ocr_res.jpg')
    except Exception as e:
        raise e

if __name__ == '__main__':
	main()
