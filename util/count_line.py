# -*- coding: UTF-8 -*-
import os
import sys
import re
import codecs
import traceback
import chardet

_recursive = False
_filter = ''
_ignoreDir = []

def countFileRaw(bf):
    cnt = 0
    with open(bf, 'rb') as fp:
        buf = fp.read()
        for ch in buf:
            if ch == ord('\n'):
                cnt += 1
    return cnt

def countFile(bf):
    encoding = 'utf-8'
    with open(bf, 'rb') as fp:
        ret = chardet.detect(fp.read())
        encoding = ret['encoding']
        fp.close()
    cnt = 0
    try:
        with codecs.open(bf, 'r', encoding) as f:
            for line in f:
                cnt += 1
    except Exception as e:
        #traceback.print_stack()
        print(e)
        print("Error counting: " + bf)

    #print('%s -> %d' % (bf, cnt))
    return cnt


def isAcceptedFile(bf):
    if (len(_filter) != 0):
        return re.match(_filter, bf, re.IGNORECASE) != None
    return True

def isAcceptedDir(dir):
    return _recursive and (dir.split('\\')[-1] not in _ignoreDir) and os.path.isdir(dir)

def countDir(basedir):
    cnt = 0
    basefiles = []
    for fn in os.listdir(basedir):
        basefiles.append(fn.lower())

    for bf in basefiles:
        fullPath = basedir + '\\' + bf
        if isAcceptedDir(fullPath):
            cnt += countDir(fullPath)
        elif isAcceptedFile(bf):
            cnt += countFileRaw(fullPath)
        else:
            #print('skip: ' + fullPath)
            pass
    print('Dir %s -> %d' % (basedir, cnt))
    return cnt


def main():
    global _filter, _recursive, _ignoreDir
    basedir = sys.argv[1]
    for i in range(2, len(sys.argv)):
        v = sys.argv[i].lower()
        if v == '-r':
            _recursive = True
        elif v == '-f':
            _filter = sys.argv[i+1]
            print(_filter)
        elif v == '-i':
            for it in sys.argv[i+1].split(','):
                _ignoreDir.append(it.lower())
    print(_filter)
    print(_ignoreDir)
    cnt = countDir(basedir)
    print("Total line: %d" % (cnt))


def usage():
    print("Usage: count_line base-dir [-r] [-f filename-filter]")


if __name__ == '__main__':
    main()
