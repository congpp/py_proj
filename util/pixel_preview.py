import os
import cv2
import numpy as np
from functools import partial

_W = 896
_H = 596

def imgFromRGBA(f: str, w, h):
    img = np.zeros([h, w, 4], np.uint8)
    with open(f, 'rb') as fp:
        for y in range(0, h):
            for x in range(0, w):
                buf = fp.read(4)
                img[y, x, 0] = buf[0]
                img[y, x, 1] = buf[1]
                img[y, x, 2] = buf[2]
                img[y, x, 3] = buf[3]
    return img


d = 'h:\\'
fl = os.listdir(d)
cnt = 0
for f in fl:
    if f.endswith('.rgba'):
        img = imgFromRGBA(d+f, _W, _H)
        cv2.imshow(f, img)
        cnt+=1
        if cnt == 10:
            cv2.waitKey(0)
            cnt = 0
if cnt > 0:
    cv2.waitKey(0)
