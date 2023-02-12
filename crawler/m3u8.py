import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import threading
import configparser
import urllib3

MAX_TASK = 5
MAX_THREAD_PER_TASK = 8

urllib3.disable_warnings()

tasks = [
    {
        'taskname': r'XXX-AV-24295',
        'url': r'https://k-3325-bbg.thisiscdn.com/bcdn_token=2AERvxUDKCUwKEUF9kvc4ro-xw6Hq8q855PGZtu4wlM&expires=1676371224&token_path=%2F861a3301-3579-4515-90cc-0bb438ae86d6%2F/861a3301-3579-4515-90cc-0bb438ae86d6/1280x720/',
        'begin-index': 1,
        'end-index': 478,
        'savepath': r'',
        'filename': r'video#IDX#.ts',
        'savename': r'XXX-AV-24295.mp4',
        'header': {
            'authority': r'k-3325-bbg.thisiscdn.com',
            'accept': r'*/*',
            'accept-language': r'zh-CN,zh;q=0.9',
            'origin': r'https://missav.com',
            'referer': r'https://missav.com/cn/XXX-AV-24295',
            'sec-ch-ua': r'"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': r'?0',
            'sec-ch-ua-platform': r'"Windows"',
            'sec-fetch-dest': r'empty',
            'sec-fetch-mode': r'cors',
            'sec-fetch-site': r'cross-site',
            'user-agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        }
    },
]

'''
outputdir: 
  savepath/taskname/
structure:
|-- filename
|-- log/
|-- ts/
'''


class DownloadTask:
    jobs = []
    lock = threading.Lock()

    def __init__(self, task) -> None:
        self.task = task
        self.outdir = task['savepath'] + task['taskname']
        self.tsdir = self.outdir + os.path.sep + 'ts'
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        if not os.path.exists(self.tsdir):
            os.mkdir(self.tsdir)

        inifile = self.getCfgFile()
        self.ini = configparser.ConfigParser()
        if os.path.exists(inifile):
            self.ini.read(inifile, 'utf-8')
        else:
            self.__saveCfgFile()

    def getUrl(self, i: int):
        url = str(self.task['url'])
        filename = str(self.task['filename']).replace('#IDX#', str(i))
        if not url.endswith('/'):
            return url + '/' + filename
        return url + filename

    def getSaveFile(self, i: int):
        return self.tsdir + os.path.sep + str(self.task['filename']).replace('#IDX#', str(i))

    def getCfgFile(self):
        return self.outdir + os.path.sep + 'cfg.ini'

    def __getSectionName(self, i: int) -> str:
        return 'video' + str(i)

    def __saveCfgFile(self):
        with open(self.getCfgFile(), 'w', encoding='utf-8') as f:
            self.ini.write(f)
            f.close()

    def __isComplete(self, i: int) -> bool:
        try:
            self.lock.acquire()
            secname = self.__getSectionName(i)
            if not secname in self.ini.sections():
                return False
            if 1 == self.ini.getint(secname, 'ok'):
                filename = self.getSaveFile(i)
                if os.path.exists(filename):
                    return True
            return False
        except Exception as e:
            print("read ini error: ", e)
            return False
        finally:
            self.lock.release()

    def __writeResult(self, i: int, ok: bool, sz: int = 0) -> bool:
        try:
            #print('write res: ', i, ok, sz)
            self.lock.acquire()
            secname = self.__getSectionName(i)
            if not secname in self.ini.sections():
                self.ini.add_section(secname)
            self.ini.set(secname, 'ok', '1' if ok else '0')
            self.ini.set(secname, 'size', '%d' % (sz))
            self.__saveCfgFile()
        except Exception as e:
            print("write ini error: ", e)
            return False
        finally:
            self.lock.release()

    def __download(self, i: int):
        try:
            if self.__isComplete(i):
                print(self.getSaveFile(i) + ' already saved!')
                return
            print('Thread %d: get %s' %
                (threading.current_thread().ident, self.getSaveFile(i)))
            req = requests.get(self.getUrl(i), headers=self.task['header'], verify=False)
            with open(self.getSaveFile(i), mode='wb') as f:
               f.write(req.content)
               self.__writeResult(i, True, len(req.content))
        except Exception as e:
            print(e)
            self.__writeResult(i, False)

    def __run(self):
        for r in range(0, 3):
            print('start: ', r)
            pool = ThreadPoolExecutor(MAX_THREAD_PER_TASK)
            jobs=[]
            for i in range(self.task['begin-index'], self.task['end-index'] + 1):
                job = pool.submit(self.__download, i)
                jobs.append(job)

            print('wait: ', r)
            wait(jobs, return_when=ALL_COMPLETED)
            if self.isFinished():
                return True

            pool.shutdown(False)
            time.sleep(5)

        print(self.task['taskname'] + ' is not completed!')
        return False

    def start(self):
        try:
            if not self.__run():
                return

            target = self.outdir + os.path.sep + self.task['savename']
            print('merge into: ', target)
            with open(target, 'wb') as f:
               for i in range(self.task['begin-index'], self.task['end-index'] + 1):
                   print('merging: ', self.getSaveFile(i))
                   with open(self.getSaveFile(i), 'rb') as tsf:
                       f.write(tsf.read())
        except Exception as e:
            print(e)


    def isFinished(self):
        for i in range(self.task['begin-index'], self.task['end-index'] + 1):
            if not self.__isComplete(i):
                return False

        return True

    def getProgress(self):
        prog = 0
        for i in range(self.task['begin-index'], self.task['end-index'] + 1):
            prog += 1 if self.__isComplete(i) else 0
        return (prog * 100.0 / self.task['end-index']) if self.task['end-index'] > 0 else 0


def downloadTask(dt: DownloadTask):
    print("Thread %d: %s" % (threading.current_thread().ident, dt.outdir))
    dt.start()


if __name__ == '__main__':
    jobs = []
    pool = ThreadPoolExecutor(max_workers=MAX_TASK)
    for t in tasks:
        dt = DownloadTask(t)
        if (dt.isFinished()):
            print(t['taskname'] + " is finished!")
            continue
        job = pool.submit(downloadTask, dt)
        jobs.append(job)
    wait(jobs, return_when=ALL_COMPLETED)

    print('exit')

