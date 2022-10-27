# -*- coding: UTF-8 -*-
import re
import sys
import os
import time
from traceback import print_stack

def printLoading(timeout = 1.0, interval = 0.2):
    ch = ('— ', '\\ ', '| ', '/ ')
    i, t = 0, time.time()
    while time.time() - t < timeout:
        print('\r'+(ch[i%len(ch)] * 5), end='', flush=True)
        i += 1
        time.sleep(interval)
    print('\r' + ' ' * 10)

class Item:
    def __init__(self, name, val) -> None:
        self.name = name
        self.val = val[0]
        self.bound = val[1]

    def __str__(self) -> str:
        return "%-8s%8.2f   ~%8.2f" % (self.name, self.val - self.bound, self.val + self.bound)

    def check(self, val):
        if val > self.val + self.bound:
            return 2
        if val > self.val + self.bound * 0.1:
            return 1
        if val < self.val - self.bound:
            return 4
        if val < self.val - self.bound * 0.1:
            return 3
        return 0


class BabyInfo:
    def __init__(self, bpd, ac, fl, hc) -> None:
        self.bpd = Item('BPD', bpd)
        self.ac = Item('AC', ac)
        self.fl = Item('FL', fl)
        self.hc = Item('HC', hc)

    def __str__(self) -> str:
        return '    %s\n    %s\n    %s\n    %s\n' % (self.bpd, self.ac, self.fl, self.hc)

    def check(self, bpd=0, ac=0, fl=0, hc=0):
        print('疯狂计算中\n')
        printLoading(5)
        print('你的宝宝：')
        if bpd > 0:
            ret = self.bpd.check(bpd)
            info = ['正常，标准头', '正常范围内偏大，头有点大，据说比较聪明', '异常数值，过大，头太大了，三鹿奶粉喝多了吧',
                    '正常范围内偏小，头比较小，小一点容易生喔', '异常数值，太小，头那么小，营养不良吗']
            print('BPD = %.2fcm, %s' %
                  (bpd, info[ret]))
        if ac > 0:
            ret = self.ac.check(ac)
            info = ['正常，标准肚', '正常范围内偏大，有点小肚腩，应该比较可爱吧', '异常数值，太大了，超级大肚腩、大胖子',
                    '正常范围内偏小，小蛮腰，瘦瘦的，应该身材不错', '异常数值，太小了，肚子都饿扁了，赶紧多吃有营养的东西点吧']
            print('AC = %.2fcm, %s' % (ac, info[ret]))
        if fl > 0:
            ret = self.fl.check(fl)
            info = ['正常，标准腿', '正常范围内偏大了，是个大长腿', '异常数值，腿那么长，得生出一个姚明？',
                    '正常范围内偏小，小短腿，跑不快，不太适合当运动员', '异常数值，太短了这腿，遗传了谁的小短腿？赶紧补钙去']
            print('FL = %.2fcm, %s' % (fl, info[ret]))
        if hc > 0:
            ret = self.hc.check(hc)
            info = ['正常，标准头', '正常范围内偏大，头有点大，出生时稍微用点力了',
                    '异常数值，过大，头太大了，可能不能顺产了', '正常范围内偏小，头比较小，易生养', '异常数值，太小，头那么小，医生都头疼']
            print('HC = %.2f, %s' % (hc, info[ret]))


_MINWEEK = 12
_BABYINFOS = {
    # 孕周(龄) 双顶径BPD(cm) 腹围AC(cm) 股骨长FRL(cm) 头围HC(cm)
    13: BabyInfo((2.52, 0.25), (6.90, 1.65), (1.17, 0.31), (7.2, 0.2)),
    14: BabyInfo((2.83, 0.57), (7.77, 1.82), (1.38, 0.48), (8.9, 0.2)),
    15: BabyInfo((3.23, 0.51), (9.13, 1.56), (1.74, 0.58), (10.5, 0.2)),
    16: BabyInfo((3.62, 0.58), (10.32, 1.92), (2.10, 0.51), (12, 0.2)),
    17: BabyInfo((3.97, 0.44), (11.49, 1.62), (2.52, 0.44), (13.5, 0.2)),
    18: BabyInfo((4.25, 0.53), (12.41, 1.89), (2.71, 0.46), (14.9, 0.2)),
    19: BabyInfo((4.52, 0.53), (13.59, 2.30), (3.03, 0.50), (16.2, 0.2)),
    20: BabyInfo((4.88, 0.58), (14.80, 1.89), (3.35, 0.47), (17.5, 0.2)),
    21: BabyInfo((5.22, 0.42), (15.62, 1.84), (3.64, 0.40), (18.7, 0.2)),
    22: BabyInfo((5.45, 0.57), (16.70, 2.23), (3.82, 0.47), (19.8, 0.2)),
    23: BabyInfo((5.80, 0.44), (17.90, 1.85), (4.21, 0.41), (20.9, 0.2)),
    24: BabyInfo((6.05, 0.50), (18.74, 2.23), (4.36, 0.51), (22, 0.2)),
    25: BabyInfo((6.39, 0.70), (19.64, 2.20), (4.65, 0.42), (23.0, 0.2)),
    26: BabyInfo((6.68, 0.61), (21.62, 2.30), (4.87, 0.41), (23.9, 0.2)),
    27: BabyInfo((6.98, 0.57), (21.81, 2.12), (5.10, 0.41), (24.9, 0.2)),
    28: BabyInfo((7.24, 0.65), (22.86, 2.41), (5.35, 0.55), (25.8, 0.2)),
    29: BabyInfo((7.50, 0.65), (23.71, 1.50), (5.61, 0.44), (26.6, 0.2)),
    30: BabyInfo((7.83, 0.62), (24.88, 2.03), (5.77, 0.47), (27.5, 0.2)),
    31: BabyInfo((8.06, 0.60), (25.78, 2.32), (6.03, 0.38), (28.3, 0.2)),
    32: BabyInfo((8.17, 0.65), (26.20, 2.33), (6.43, 0.49), (29.0, 0.2)),
    33: BabyInfo((8.50, 0.47), (27.78, 2.30), (6.52, 0.46), (29.8, 0.2)),
    34: BabyInfo((8.61, 0.63), (27.99, 2.55), (6.62, 0.43), (30.5, 0.2)),
    35: BabyInfo((8.70, 0.55), (28.74, 2.88), (6.71, 0.45), (31.2, 0.2)),
    36: BabyInfo((8.81, 0.57), (29.44, 2.83), (6.95, 0.47), (31.9, 0.2)),
    37: BabyInfo((9.00, 0.63), (30.14, 2.17), (7.10, 0.52), (32.6, 0.2)),
    38: BabyInfo((9.08, 0.59), (30.63, 2.8), (7.20, 0.43), (33.3, 0.2)),
    39: BabyInfo((9.21, 0.59), (31.34, 3.12), (7.34, 0.53), (33.9, 0.2)),
    40: BabyInfo((9.28, 0.50), (31.49, 2.79), (7.4, 0.53), (34.5, 0.2)),
}


def usage():
    print(
        'Usage: \n    python mummy.py week current-week [bdp cm] [ac cm] [fl cm] [hc cm]')
    print('Example:\n    python mummy.py week 21 bpd 8.5\n')


def main():
    print('==================================')
    print('陈小帅孕宝助手 v1.1')
    print('Copyright (C) 2022 chenxiaoshuai')
    print('..................................')
    argc = len(sys.argv)
    argv = sys.argv
    i, week, bpd, ac, fl, hc = 0, 0, 0, 0, 0, 0
    while i < argc:
        k = argv[i].lower()
        if k == 'week':
            week = float(argv[i+1])
        elif k == 'bpd':
            bpd = float(argv[i+1])
        elif k == 'ac':
            ac = float(argv[i+1])
        elif k == 'fl':
            fl = float(argv[i+1])
        elif k == 'hc':
            hc = float(argv[i+1])
        i = i+1

    if 1 <= week <= 12:
        print('12周以下，貌似不必关心这些参数')
        return
    if argc > 4 and week in _BABYINFOS:
        print('孕妈 %d 周, 宝宝参数参考范围：' % week)
        print(_BABYINFOS[week])
        _BABYINFOS[week].check(bpd, ac, fl, hc)
        return
    raise (Exception('error param'))


if __name__ == "__main__":
    try:
        main()
        print('\n\n')
    except:
        print_stack()
        usage()
