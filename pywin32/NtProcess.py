# -*- coding: UTF-8 -*-
from ctypes import *
from ctypes.wintypes import *
import win32api
import copy
import re

class PROCESSENTRY32(Structure):
    _fields_ = [
    ('dwSize', DWORD),
    ('cntUsage', DWORD),
    ('th32ProcessID', DWORD),
    ('th32DefaultHeapID', LPVOID),
    ('th32ModuleID', DWORD),
    ('cntThreads', DWORD),
    ('th32ParentProcessID', DWORD),
    ('pcPriClassBase', LONG),
    ('dwFlags', DWORD),
    ('szExeFile', c_char * MAX_PATH)]
    def clone(self):
        obj = PROCESSENTRY32()
        obj.dwSize = self.dwSize
        obj.cntUsage = self.cntUsage
        obj.th32ProcessID = self.th32ProcessID
        obj.th32DefaultHeapID = self.th32DefaultHeapID
        obj.th32ModuleID = self.th32ModuleID
        obj.cntThreads = self.cntThreads
        obj.th32ParentProcessID = self.th32ParentProcessID
        obj.pcPriClassBase = self.pcPriClassBase
        obj.dwFlags = self.dwFlags
        obj.szExeFile = self.szExeFile
        return obj

class THREADENTRY32(Structure):
    _fields_ = [
    ('dwSize', DWORD),
    ('cntUsage', DWORD),
    ('th32ThreadID', DWORD),
    ('th32OwnerProcessID', DWORD),
    ('tpBasePri', LONG),
    ('tpDeltaPri', LONG),
    ('dwFlags', DWORD)]
    def clone(self):
        obj = PROCESSENTRY32()
        obj.dwSize = self.dwSize
        obj.cntUsage = self.cntUsage
        obj.th32ThreadID = self.th32ThreadID
        obj.th32OwnerProcessID = self.th32OwnerProcessID
        obj.tpBasePri = self.tpBasePri
        obj.tpDeltaPri = self.tpDeltaPri
        obj.dwFlags = self.dwFlags
        return obj

TH32CS_SNAPHEAPLIST   = 0x00000001
TH32CS_SNAPPROCESS    = 0x00000002
TH32CS_SNAPTHREAD     = 0x00000004
TH32CS_SNAPMODULE     = 0x00000008
TH32CS_SNAPMODULE32   = 0x00000010
TH32CS_SNAPALL        = 0x0000000F
TH32CS_INHERIT        = 0x80000000


PROCESS_TERMINATE                  = (0x0001)
PROCESS_CREATE_THREAD              = (0x0002)
PROCESS_SET_SESSIONID              = (0x0004)
PROCESS_VM_OPERATION               = (0x0008)
PROCESS_VM_READ                    = (0x0010)
PROCESS_VM_WRITE                   = (0x0020)
PROCESS_DUP_HANDLE                 = (0x0040)
PROCESS_CREATE_PROCESS             = (0x0080)
PROCESS_SET_QUOTA                  = (0x0100)
PROCESS_SET_INFORMATION            = (0x0200)
PROCESS_QUERY_INFORMATION          = (0x0400)
PROCESS_SUSPEND_RESUME             = (0x0800)
PROCESS_QUERY_LIMITED_INFORMATION  = (0x1000)
PROCESS_ALL_ACCESS                 = (0x1FFFFF)

class ProcessMonitor:
    class ProcessNotFoundError(Exception): pass
    class TH32Error(Exception): pass

    def __init__(self):
        self.__NTDLL = WinDLL('Kernel32.dll')
        #HANDLE CreateToolhelp32Snapshot([in] DWORD dwFlags,[in] DWORD th32ProcessID);
        self.__NTDLL.CreateToolhelp32Snapshot.argtypes = [DWORD, DWORD]
        self.__NTDLL.CreateToolhelp32Snapshot.restypes = [HANDLE]
        self.__NTDLL.Process32First.argtypes = [HANDLE, LPVOID]
        self.__NTDLL.Process32First.restypes = [BOOL]
        self.__NTDLL.Process32Next.argtypes = [HANDLE, LPVOID]
        self.__NTDLL.Process32Next.restypes = [BOOL]
        #HANDLE CreateToolhelp32Snapshot(DWORD dwFlags, DWORD th32ProcessID)
        self.__NTDLL.Thread32First.argtypes = [HANDLE, LPVOID]
        self.__NTDLL.Thread32First.restypes = [BOOL]
        self.__NTDLL.Thread32Next.argtypes = [HANDLE, LPVOID]
        self.__NTDLL.Thread32Next.restypes = [BOOL]

    def getProcessEntries(self, filter_reg=''):
        procInfo=[]
        pe32 = PROCESSENTRY32()
        pe32.dwSize = 556
        hSnap = self.__NTDLL.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if hSnap == -1:
            raise self.TH32Error, "error CreateToolhelp32Snapshot"

        if filter_reg != '':
            regex = re.compile(filter_reg, re.IGNORECASE)
        
        bMore = self.__NTDLL.Process32First(hSnap, byref(pe32))
        while bMore:
            if filter_reg == '' or regex.match(str(pe32.szExeFile)) != None:
                procInfo.append(pe32.clone())
            bMore = self.__NTDLL.Process32Next(hSnap, byref(pe32))

        win32api.CloseHandle(hSnap)
        return procInfo

    def openProcessByName(self, exeName, flags=PROCESS_ALL_ACCESS):
        procInfo = self.getProcessEntries(exeName)
        if len(procInfo) == 0:
            raise self.ProcessNotFoundError, exeName

        hProcesses=[]
        for pe32 in procInfo:
            hProcesses.append(win32api.OpenProcess(flags, pe32.th32ProcessID))
        return hProcesses

    def getThreadEntries(self, processID=-1):
        te32 = THREADENTRY32()
        te32.dwSize = 28
        hSnap = self.__NTDLL.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
        if hSnap == -1:
            raise self.TH32Error, "error CreateToolhelp32Snapshot"
        
        threadInfo=[]
        bMore = self.__NTDLL.Thread32First(hSnap, byref(te32))
        while bMore:
            if processID==te32.th32OwnerProcessID or processID == -1:
                threadInfo.append(te32.clone())
            bMore = self.__NTDLL.Thread32Next(hSnap, byref(te32))

        win32api.CloseHandle(hSnap)
        return threadInfo

    def getProcessThread(self, exeName):
        procInfo = self.getProcessEntries(exeName)
        if len(procInfo) == 0:
            raise self.ProcessNotFoundError, exeName

        pid=set()
        for pe32 in procInfo:
            pid.add(pe32.th32ProcessID)

        threadInfo=[]
        te32 = THREADENTRY32()
        te32.dwSize = 28
        hSnap = self.__NTDLL.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
        if hSnap == -1:
            raise self.TH32Error, "error CreateToolhelp32Snapshot"
        
        bMore = self.__NTDLL.Thread32First(hSnap, byref(te32))
        while bMore:
            if te32.th32OwnerProcessID in pid:
                threadInfo.append(te32.clone())
            bMore = self.__NTDLL.Thread32Next(hSnap, byref(te32))

        win32api.CloseHandle(hSnap)
        return threadInfo

class ProcessController:
    def __init__(self, exeName):
        self._exeName = exeName
        self._hProcesses = ProcessUtil().openProcessByName(self._exeName)
        self.loadNtDLL()

    def __del__(self):
        self.unloadNtDLL()

    #DWORD WINAPI NtResumeProcess(HANDLE hProcess);
    #DWORD WINAPI NtSuspendProcess(HANDLE hProcess);
    def loadNtDLL(self):
        self.__NTDLL = WinDLL('ntdll.dll')
        self.__NTDLL.NtResumeProcess.argtypes = [HANDLE]
        self.__NTDLL.NtResumeProcess.restypes = [DWORD]
        self.__NTDLL.NtSuspendProcess.argtypes = [HANDLE]
        self.__NTDLL.NtSuspendProcess.restypes = [DWORD]
        self.__NTDLL.NtTerminateProcess.argtypes = [HANDLE, UINT]
        self.__NTDLL.NtTerminateProcess.restypes = [DWORD]

    def suspendProcess(self):
        cnt = 0
        for h in self._hProcesses:
            if 0 == self.__NTDLL.NtSuspendProcess(int(h)):
                cnt += 1

        print("Suspend process %d" % {cnt})
        return cnt == len(self._hProcesses);

    def resumeProcess(self):
        cnt = 0
        for h in self._hProcesses:
            if 0 == self.__NTDLL.NtResumeProcess(int(h)):
                cnt += 1

        print("Resume process %d" % {cnt})
        return cnt == len(self._hProcesses)

    def terminateProcess(self):
        cnt = 0
        for h in self._hProcesses:
            if 0 == self.__NTDLL.NtTerminateProcess(int(h)):
                cnt += 1

        print("kill process", cnt);
        return cnt == len(self._hProcesses);

    def unloadNtDLL(self):
        for h in self._hProcesses:
            win32api.CloseHandle(h)


class ProcessAutoSuspendResume:
    def __init__(self, exeName):
        self._procCtrl = ProcessController(exeName)
        self._procCtrl.suspendProcess()

    def __del__(self):
        self._procCtrl.resumeProcess()