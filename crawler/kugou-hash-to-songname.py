#!/usr/bin/python
# -*- coding: UTF-8 -*-

#酷狗歌曲hashid转名称
#用于转换酷狗temp目录的文件名
import sys
import os
import requests
import re
from requests.cookies import RequestsCookieJar
import json
url_w = "https://www.kugou.com/yy/index.php?r=play/getdata&hash={HASHID}"
url_m = "http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={HASHID}"

cookie = RequestsCookieJar()
cookie.set("kg_mid", "2333")
isRecursive = False

def getSongNameM(hashID):
    url2 = url_m
    url2 = url2.replace("{HASHID}", hashID)
    res = requests.post(url2, cookies=cookie)

    #{
    #    // ...
    #    "fileName": "安心音乐 - 第 45 集 大自然的下雨声-治愈失眠的深度催眠轻音乐",
    #    //...
    #    "album_img": "http://imge.kugou.com/stdmusic/{size}/20200410/20200410172721673519.jpg",
    #}
    try:
        js = json.loads(res.text)
        return js["fileName"]
    except Exception, e:
        print(e)
        return ""

def getSongNameW(hashID):
    url2 = url_w
    url2 = url2.replace("{HASHID}", hashID)
    res = requests.post(url2, cookies=cookie)

    #
    #{
    #    "status": 1,
    #    "err_code": 0,
    #    "data": {
    #        "hash": "1035269c05791f1665e36dffe478326c",
    #        "audio_name": "大壮 - 我们不一样",
    #        ...
    #    }
    #}
    #
    #print(res.text)
    try:
        js = json.loads(res.text)
        return js["data"]["audio_name"]
    except Exception, e:
        print(e)
        return ""


def getSongName(hashID):
    songName = getSongNameW(hashID)
    if len(songName) == 0:
        songName = getSongNameM(hashID);
        
    for ch in "\\/:*?\"<>|" :
        songName = songName.replace(ch, "");
        
    print(hashID + " => " + songName.encode("gbk", 'ignore'))
    return songName;

def renameDir(dirPath):
    for f in os.listdir(dirPath):
        if os.path.isdir(f) and isRecursive:
            renameDir(dirPath + "\\" + f)
        else:
            renameFile(dirPath + "\\" + f)
        

def getUniqueFileName(dirPath, fileName, fileExt):
    i=1
    newFilePath = dirPath + "\\" + fileName + "." + fileExt;
    while os.path.exists(newFilePath):
        newFilePath = dirPath + "\\" + fileName + "(" + str(i) + ")." + fileExt;
        i = i+1
    return newFilePath

def renameFile(filePath):
    try:
        dirPath = os.path.dirname(filePath)
        fileName = os.path.basename(filePath)
        nameset = fileName.split(".")
        songName = ""
        if re.match("[0-9a-f]{32}", nameset[0]):
            songName = getSongName(nameset[0])
        if len(songName) > 0 :
            newFilePath = getUniqueFileName(dirPath, songName, nameset[1]);
            print(filePath + " rename to " + newFilePath.encode("gbk", 'ignore'))
            os.rename(filePath, newFilePath)
    except Exception, e:
        print(e)
        print("Error skip " + filePath)

if __name__ == '__main__':
    inputFile = sys.argv[1]
    print(inputFile)
    if os.path.isdir(inputFile):
        renameDir(inputFile)
    else:
        renameFile(inputFile);
