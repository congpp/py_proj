# -*- coding: UTF-8 -*-
from file_watcher import DirWatcher
import sys
import os
import time
import threading
import re

class DuiSkinWatcher:
    def __init__(self) -> None:    
        self.exePath = r"D:\CYC\DataRecovery\bin\Debug"
        self.exeFile = r"SkinPreview.exe"
        self.skinFile = ''
        self.watchPath = ''
        self.othercmd = ''
        self.x = 10
        self.y = 200

    def findPreviewExe(self):
        if not os.path.exists(self.skinFile):
            return

        head=[]
        with open(self.skinFile, encoding='utf-8') as f:
            head = f.readlines(10)
        reg = re.compile(r'<!--.*@preview="(.*?)".*-->')
        for line in head:
            m = reg.match(line)
            if m and os.path.exists(m[1]):
                self.exePath = m[1]
                self.exeFile = os.path.basename(self.exePath)
                print(f'preview: {self.exePath}')
            regX = re.compile(r'<!--.*@x="(\d+)".*-->')
            m = regX.match(line)
            if m:
                self.x = int(m[1])
            regY = re.compile(r'<!--.*@y="(\d+)".*-->')
            m = regY.match(line)
            if m:
                self.y = int(m[1])
            print(f'preview x: {self.x}, {self.y}')
            break

    def onFileChanged(self, fileName):
        cmd = "tskill " + self.exeFile.rstrip(".exe")
        print(f'run: {cmd}')
        os.system(cmd)
        time.sleep(0.25)
        fullpath=os.path.join(self.exePath, self.exeFile)
        cmd = f'start {fullpath} "{self.skinFile}" -p {self.x} {self.y} {self.othercmd}'
        print(f'run: {cmd}')
        os.system(cmd)

    def run(self):
        self.skinFile = sys.argv[1].strip(' ').strip('"')
        print('Load skin: ' + self.skinFile)
        if not os.path.exists(self.skinFile):
            raise Exception("file not found: " + self.skinFile)
        
        self.watchPath = os.path.dirname(self.skinFile)
        self.findPreviewExe()

        for cmd in sys.argv[2:]:
            if cmd.lower() == '-once':
                return

        print('Watching: ' + self.watchPath)
        DirWatcher().start(self.watchPath, self.onFileChanged)


if __name__ == "__main__":
    obj = DuiSkinWatcher()
    obj.run()