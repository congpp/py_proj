# -*- coding: UTF-8 -*-
import os
import sys
import re

_r = False
_f = ''


def diffFile(bf, df):
    cmd = 'TortoiseMerge.exe /base "%s" /mine "%s"' % (
        bf.replace('/', '\\'), df.replace('/', '\\'))
    print(cmd)
    os.system(cmd)


def filter(bf, df):
    if (len(_f) != 0):
        return re.match(_f, bf, re.IGNORECASE) != None and bf.lower() == df.lower()
    return bf.lower() == df.lower()


def diffDir(basedir, diffdir):
    print('diffDir %s %s' % (basedir, diffdir))
    basefiles = []
    difffiles = []
    for fn in os.listdir(basedir):
        basefiles.append(fn.lower())

    for fn in os.listdir(diffdir):
        difffiles.append(fn.lower())

    for bf in basefiles:
        for df in difffiles:
            bff, dff = basedir + '\\' + bf, diffdir + '\\' + df
            if bf == df and os.path.isdir(bff):
                if _r:
                    diffDir(bff, dff)
                break
            elif filter(bf, df):
                print(bff, dff)
                diffFile(bff, dff)
                break


def main():
    global _f, _r
    basedir = sys.argv[1]
    diffdir = sys.argv[2]
    for i in range(3, len(sys.argv)):
        v = sys.argv[i].lower()
        if v == '-r':
            _r = True
        elif v == '-f':
            _f = sys.argv[i+1]
    print(_f)
    diffDir(basedir, diffdir)


def usage():
    print("Usage: diff_dir base-dir diff-dir")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        usage()
