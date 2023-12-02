# -*- coding: UTF-8 -*-
import fileWatcher
import sys
import os
import time
import threading

exePath = r"D:\CYC\DataRecovery\bin\Debug"
exeFile = r"SouiSkinPreview.exe"
skinFile = None
othercmd = ''

def onFileChanged(fileName, action, fileNameNew):
    os.system("tskill " + exeFile.rstrip(".exe"))
    os.system(r"start %s\%s %s -skia -p 10 200 %s" % (exePath, exeFile, skinFile, othercmd))

def main():
    global skinFile, othercmd
    skinFile = sys.argv[1].strip(' ').strip('"')
    print('Load skin: ' + skinFile)
    if not os.path.exists(skinFile):
        raise Exception("file not found: " + skinFile)
    skinPath = os.path.dirname(skinFile)
    skinPath = os.path.join(skinPath, (sys.argv[2].strip(' ').strip('"').strip(os.path.sep)))
    print('Watching: ' + skinPath)
    for cmd in sys.argv[3:]:
        othercmd += cmd
        othercmd += ' '
    onFileChanged(skinFile, 1, None)
    watcher = fileWatcher.DirWatcher()
    t = threading.Thread(target=lambda:{watcher.start(skinPath, onFileChanged)})
    t.start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        time.sleep(5)