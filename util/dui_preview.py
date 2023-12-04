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
        with open(self.skinFile) as f:
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

    def onFileChanged(self, fileName, action, fileNameNew):
        cmd = "tskill " + self.exeFile.rstrip(".exe")
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
        
        self.watchPath = os.path.dirname(self.skinFile)
        self.findPreviewExe()

        for cmd in sys.argv[2:]:
            if cmd.lower() == '-once':
                return

        print('Watching: ' + self.watchPath)
        self.othercmd = ' '.join(sys.argv[2:])
        
        self.onFileChanged(self.skinFile, 1, None)
        watcher = DirWatcher()
        self.t = threading.Thread(target=lambda:{watcher.start(self.watchPath, self.onFileChanged)})
        self.t.start()


if __name__ == "__main__":
    obj = DuiSkinWatcher()
    obj.run()