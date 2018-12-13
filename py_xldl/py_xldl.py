#coding=utf-8

import pytorrent
import bencode
import time
import hashlib
import base64

from xldl import XLDL

xl=XLDL('xldl.dll')
xl.Init()

#获取参数
torrentName = 'E:/Git/Conn/py_proj/py_xldl/torrent/test.torrent'

# ret = xl.CreateTaskByThunder(torrentName, 'E:/Git/Conn/py_proj/py_xldl/torrent/', '', '', '')
ret = xl.CreateTaskByURL('http://softdl.360tpcdn.com/KYSetup/KYSetup_3.0.1.2.exe', 'E:/Git/Conn/py_proj/py_xldl/torrent/', u'中文.exe', 1)
print(ret)

ret = xl.TaskStart(ret)
print(ret)

#读取种子文件
torrent = open(torrentName, 'rb').read()
#计算meta数据

coder = bencode.Bencoder()

metadata = coder.decode(torrent)
hashcontents = coder.encode(metadata['info'])
#print(metadata['info'])
digest = hashlib.sha1(hashcontents).digest()
b32hash = base64.b32encode(digest)
#打印
print 'magnet:?xt=urn:btih:%s' % b32hash

# try:
# 	t=pytorrent.Torrent()
# 	t.load("torrent/test.torrent")  #your torrent file
# 	print t.data["info"]["name"].decode("utf-8")
# 	files=t.data["info"]["files"]
# 	for item in files:
# 	    print item["path"][0].decode("utf-8")
# 	t.data["info"]["name"]="my_name" #change info. some software may read ["info"]["name.utf-8"]
# 	t.dump("dump.torrent")  #the new torrent file
# except Exception as e:
# 	raise e


time.sleep(100)

xl.UnInit()
