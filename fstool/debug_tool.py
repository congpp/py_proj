
from easy_struct import *
import time
import colorama

colorama.init(True)


class Logger:
    AUTO_TIMESTAMP = False
    __LOG_LEVEL_INFO = 0x01
    __LOG_LEVEL_OK = 0x02
    __LOG_LEVEL_WARN = 0x04
    __LOG_LEVEL_ERROR = 0x08
    LOG_LEVEL = 0x0F

    @staticmethod
    def _mkmsg(msg: str):
        if Logger.AUTO_TIMESTAMP:
            t = time.time()
            return (
                time.strftime("[%Y-%m-%d %H:%M:%S.", time.localtime(t))
                + "%03d] " % (int(t * 100) % 1000)
                + str(msg)
            )
        return str(msg)

    @staticmethod
    def info(msg: str):
        if Logger.LOG_LEVEL & Logger.__LOG_LEVEL_INFO:
            print(Logger._mkmsg(msg))

    @staticmethod
    def warn(msg: str):
        if Logger.LOG_LEVEL & Logger.__LOG_LEVEL_WARN:
            print(colorama.Fore.YELLOW + Logger._mkmsg(msg))

    @staticmethod
    def err(msg: str):
        if Logger.LOG_LEVEL & Logger.__LOG_LEVEL_ERROR:
            print(colorama.Fore.RED + Logger._mkmsg(msg))

    @staticmethod
    def ok(msg: str):
        if Logger.LOG_LEVEL & Logger.__LOG_LEVEL_OK:
            print(colorama.Fore.GREEN + Logger._mkmsg(msg))


def dumpBytes(buf: bytes, linesize: int = 16):
    s = "\n"
    s1 = ""
    i = 0
    for b in range(len(buf)):
        s += "%02x " % (buf[b])
        s1 += (
            buf[b : b + 1].decode(errors="ignore")
            if buf[b : b + 1].decode(errors="ignore").isprintable()
            else "."
        )
        i += 1
        if i % linesize == 0:
            s += (" " * 4) + s1 + "\n"
            s1 = ""
    if s1:
        return s + (" " * ((linesize - i % linesize) * 3 + 4)) + s1
    else:
        return s

