# -*- coding: UTF-8 -*-
import fileWatcher
import sys
import os
import time
import threading

exePath = r"D:\CYC\DataRecovery\bin\Debug"
exeFile = r"SkinPreview.exe"
skinFile = None

def onFileChanged(fileName, action, fileNameNew):
    os.system("tskill " + exeFile.rstrip(".exe"))
    os.system(r"start %s\%s %s -p 10 200 -top" % (exePath, exeFile, skinFile))

def main():
    global skinFile
    skinFile = sys.argv[1].strip(' ').strip('"')
    if not os.path.exists(skinFile):
        raise Exception("file not found: " + skinFile)
    skinPath = skinFile[0:skinFile.rindex("\\")]
    if (len(sys.argv) > 2):
        skinPath = skinPath + sys.argv[2].strip(' ').strip('"')
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