# -*- coding: UTF-8 -*-
from file_watcher import DirWatcher
import sys
import os
import time
import re

class SouiSkinWatcher:
    def __init__(self) -> None:
        self.exePath = r""
        self.skinFile = ''
        self.watchPath = ''
        self.othercmd = ''
        self.x = 10
        self.y = 200

    def findPreviewExe(self, skinPath):
        indexFile = ''
        hasIndexFile = False
        while len(skinPath) > 3:
            indexFile = os.path.join(skinPath, 'uires.idx')
            if os.path.exists(indexFile):
                hasIndexFile = True
                self.watchPath = skinPath
                break
            skinPath = os.path.dirname(skinPath)

        if not hasIndexFile:
            return

        head=[]
        with open(indexFile) as f:
            head = f.readlines(10)
        regP = re.compile(r'<!--.*@preview="(.*?)".*-->')
        regX = re.compile(r'<!--.*@x="(\d+)".*-->')
        regY = re.compile(r'<!--.*@y="(\d+)".*-->')
        regCmd = re.compile(r'<!--.*@cmd="(.*?)".*-->')
        for line in head:
            print(line)
            m = regP.match(line)
            if m:
                p = m[1]
                #p is relative path
                if len(p) > 2 and p[1] != ':':
                    p = os.path.abspath(os.path.join(os.path.split(indexFile)[0], p))
                if os.path.exists(p):
                    self.exePath = p
                    print(f'preview: {self.exePath}')
                else:
                    print(f'preview: {p} not found!')
            m = regX.match(line)
            if m:
                self.x = int(m[1])
            m = regY.match(line)
            if m:
                self.y = int(m[1])
            print(f'preview x: {self.x}, {self.y}')
            
            m = regCmd.match(line)
            if m:
                self.othercmd = m[1]
                print(f'othercmd: {m[1]}')
            break

    def onFileChanged(self, filelist):
        if not os.path.exists(self.exePath):
            raise Exception(f'preview: {self.exePath} not found!')
        cmd = "tskill " + os.path.basename(self.exePath).rstrip(".exe")
        print(f'run: {cmd}')
        os.system(cmd)
        time.sleep(0.25)
        cmd = f"start {self.exePath} {self.skinFile} -skia -p {self.x} {self.y} {self.othercmd}"
        print(f'run: {cmd}')
        os.system(cmd)

    def run(self):
        self.skinFile = sys.argv[1].strip(' ').strip('"')
        print('Load skin: ' + self.skinFile)
        if not os.path.exists(self.skinFile):
            raise Exception("file not found: " + self.skinFile)
        
        skinPath = os.path.dirname(self.skinFile)
        self.findPreviewExe(skinPath)

        self.onFileChanged([self.skinFile])
        for cmd in sys.argv[2:]:
            if cmd.lower() == '-once':
                return

        print('Watching: ' + self.watchPath)
        DirWatcher().start(self.watchPath, self.onFileChanged)


if __name__ == "__main__":
    obj = SouiSkinWatcher()
    obj.run()