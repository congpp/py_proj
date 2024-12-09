# -*- coding: UTF-8 -*-
from ctypes import *
from ctypes.wintypes import *
import win32api
import copy
import re

_kernel32DLL = WinDLL('kernel32')

class FILETIME(Structure):
    _fields_ = [
    ('low', DWORD),
    ('high', DWORD)]
    def clone(self):
        obj = FILETIME()
        obj.low = self.low
        obj.high = self.high
        return obj
    def asInt(self):
        return (self.high << 32) | self.low
    def __str__(self) -> str:
        return str(self.asInt())
    @staticmethod
    def new(t):
        ft = FILETIME()
        ft.low = t&0xFFFFFFFF
        ft.high = t>>32
        return ft
    
class SYSTEMTIME(Structure):
    _fields_=[
    ('wYear', WORD),
    ('wMonth', WORD),
    ('wDayOfWeek', WORD),
    ('wDay', WORD),
    ('wHour', WORD),
    ('wMinute', WORD),
    ('wSecond', WORD),
    ('wMilliseconds', WORD),
    ]
    @staticmethod
    def new(yy, mm, dd, HH, MM, SS, ms):
        st = SYSTEMTIME()
        st.wYear = yy
        st.wMonth = mm
        st.wDay = dd
        st.wHour = HH
        st.wMinute = MM
        st.wSecond = SS
        st.wMilliseconds = ms
        return st
    @staticmethod
    def now():
        st = SYSTEMTIME()
        _kernel32DLL.GetSystemTime(byref(st))
        return st

    def __str__(self) -> str:
        return '%04d-%02d-%02d %02d:%02d:%02d.%03d'%(self.wYear, self.wMonth, self.wDay, self.wHour, self.wMinute, self.wSecond, self.wMilliseconds)


def formatFILETIME(t:int):
    ft = FILETIME.new(t)
    st = SYSTEMTIME()
    _kernel32DLL.FileTimeToSystemTime(byref(ft), byref(st))
    return str(st)

def testFileTime():
    st = SYSTEMTIME.now()
    print(st)

    ft = FILETIME()
    _kernel32DLL.SystemTimeToFileTime(byref(st), byref(ft))
    print(ft)

    print('===============')

    while True:
        print('input filetime>', end='')
        cmd = (input() + ' ').lower().strip()
        if cmd == 'e' or cmd == 'exit':
            break
        ft = FILETIME.new(int(cmd))
        _kernel32DLL.FileTimeToSystemTime(byref(ft), byref(st))
        print(st)

if __name__ == '__main__':
    testFileTime()
