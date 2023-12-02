# -*- coding: UTF-8 -*-
import struct
from ctypes import *
from ctypes.wintypes import *
import time

'''
typedef struct _FILE_NOTIFY_INFORMATION {
    DWORD NextEntryOffset;
    DWORD Action;
    DWORD FileNameLength;
    WCHAR FileName[1];
} FILE_NOTIFY_INFORMATION, *PFILE_NOTIFY_INFORMATION;
'''
class FILE_NOTIFY_INFORMATION(Structure):
    _fields_ = [
    ('NextEntryOffset', DWORD),
    ('Action', DWORD),
    ('FileNameLength', DWORD),
    ('FileName', WCHAR)]
    def clone(self):
        obj = FILE_NOTIFY_INFORMATION()
        obj.NextEntryOffset = self.NextEntryOffset
        obj.Action = self.Action
        obj.FileNameLength = self.FileNameLength
        obj.FileName = self.FileName
        return obj
        
'''
typedef struct _PROCESS_INFORMATION {
    HANDLE hProcess;
    HANDLE hThread;
    DWORD dwProcessId;
    DWORD dwThreadId;
} PROCESS_INFORMATION, *PPROCESS_INFORMATION, *LPPROCESS_INFORMATION;
'''
class PROCESS_INFORMATION(Structure):
    _fields_ = [
    ('hProcess', HANDLE),
    ('hThread', HANDLE),
    ('dwProcessId', DWORD),
    ('dwThreadId', DWORD)]
    def clone(self):
        obj = PROCESS_INFORMATION()
        obj.hProcess = self.hProcess
        obj.hThread = self.hThread
        obj.dwProcessId = self.dwProcessId
        obj.dwThreadId = self.dwThreadId
        return obj

GENERIC_READ                    = 0x80000000
FILE_LIST_DIRECTORY             = 0x00000001

FILE_SHARE_READ                 = 0x00000001
FILE_SHARE_WRITE                = 0x00000002
FILE_SHARE_DELETE               = 0x00000004

OPEN_EXISTING                   = DWORD(3)
FILE_FLAG_BACKUP_SEMANTICS      = 0x02000000
FILE_FLAG_OVERLAPPED            = 0x40000000
INVALID_HANDLE_VALUE            = HANDLE(-1)
FILE_NOTIFY_CHANGE_FILE_NAME    = 0x00000001
FILE_NOTIFY_CHANGE_DIR_NAME     = 0x00000002
FILE_NOTIFY_CHANGE_SIZE         = 0x00000008


FILE_ACTION_ADDED               = 0x00000001   
FILE_ACTION_REMOVED             = 0x00000002   
FILE_ACTION_MODIFIED            = 0x00000003   
FILE_ACTION_RENAMED_OLD_NAME    = 0x00000004   
FILE_ACTION_RENAMED_NEW_NAME    = 0x00000005   

BUFFER_SIZE = 1 * 1024 * 1024

class DirWatcher:
    class FatalError(Exception): pass

    def __init__(self) -> None:
        self._KERNEL32 = WinDLL('Kernel32.dll')
        #HANDLE WINAPI CreateFileA( LPCSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode,LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition, DWORD dwFlagsAndAttributes,HANDLE hTemplate)
        self._KERNEL32.CreateFileA.argtypes = [LPCSTR, DWORD, DWORD, LPVOID, DWORD, DWORD, HANDLE]
        self._KERNEL32.CreateFileA.restypes = [HANDLE]
        #HANDLE WINAPI CreateEventA( LPSECURITY_ATTRIBUTES lpEventAttributes, BOOL bManualReset, BOOL bInitialState, LPCSTR lpName )
        self._KERNEL32.CreateEventA.argtypes = [LPVOID, BOOL, BOOL, LPCSTR]
        self._KERNEL32.CreateEventA.restypes = [HANDLE]
        #BOOL WINAPI ReadDirectoryChangesW(  HANDLE hDirectory, LPVOID lpBuffer,  DWORD nBufferLength,  BOOL bWatchSubtree,  DWORD dwNotifyFilter,    LPDWORD lpBytesReturned,  LPOVERLAPPED lpOverlapped,  LPOVERLAPPED_COMPLETION_ROUTINE lpCompletionRoutine );
        self._KERNEL32.ReadDirectoryChangesW.argtypes = [HANDLE, LPVOID, DWORD, BOOL, DWORD, LPDWORD, LPVOID, LPVOID]
        self._KERNEL32.ReadDirectoryChangesW.restypes = [BOOL]
        #WINBASEAPI DWORD WINAPI WaitForSingleObject( _In_ HANDLE hHandle, _In_ DWORD dwMilliseconds )
        self._KERNEL32.WaitForSingleObject.argtypes = [HANDLE, DWORD]
        self._KERNEL32.WaitForSingleObject.restypes = [DWORD]
        #WINBASEAPI DWORD WINAPI WaitForSingleObject( _In_ HANDLE hHandle, _In_ DWORD dwMilliseconds )
        self._KERNEL32.CloseHandle.argtypes = [HANDLE]
        self._KERNEL32.CloseHandle.restypes = [BOOL]
        #DWORD GetLastError
        self._KERNEL32.GetLastError.argtypes = []
        self._KERNEL32.GetLastError.restypes = [DWORD]
        
        self._NTDLL = WinDLL('ntdll.dll')
        self._NTDLL.NtTerminateProcess.argtypes = [HANDLE, UINT]
        self._NTDLL.NtTerminateProcess.restypes = [DWORD]

    def start(self, dir, callback):
        self.dir = dir        
        self.hDir = self._KERNEL32.CreateFileA(bytes(dir, "UTF-8"), GENERIC_READ|FILE_LIST_DIRECTORY, FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE, 0, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, 0)
        if (self.hDir == INVALID_HANDLE_VALUE):
            raise self.FatalError("cannot open dir")
        
        print("hDir: 0x%x, err: %d" % (self.hDir, self._KERNEL32.GetLastError()))

        #hEvt = self._KERNEL32.CreateEventA(0, 0, 0, LPCSTR(0))
        #print("hEvt: 0x%x, err: %d" % (hEvt, self._KERNEL32.GetLastError()))

        cbRead = DWORD(0)
        buf = bytes(BUFFER_SIZE)
        while 1:
            ret = self._KERNEL32.ReadDirectoryChangesW(self.hDir, buf, BUFFER_SIZE, BOOL(1), FILE_NOTIFY_CHANGE_FILE_NAME|FILE_NOTIFY_CHANGE_DIR_NAME|FILE_NOTIFY_CHANGE_SIZE, byref(cbRead), LPVOID(0), LPVOID(0))
            print(ret)

            if not ret:
                raise self.FatalError("cannot read dir changes: %d" %(self._KERNEL32.GetLastError()))
            
            '''
            typedef struct _FILE_NOTIFY_INFORMATION {
                DWORD NextEntryOffset;
                DWORD Action;
                DWORD FileNameLength;
                WCHAR FileName[1];
            } FILE_NOTIFY_INFORMATION, *PFILE_NOTIFY_INFORMATION;
            '''
            data = buf
            while 1:
                nextOffset, action, fileNameLen = struct.unpack('lll', data[0:12])
                print("Changed: off=%d, act=%d, nameLen=%d" % (nextOffset, action, fileNameLen))

                fileName, fileNameNew = None, None
                if action == FILE_ACTION_ADDED or action == FILE_ACTION_MODIFIED or action == FILE_ACTION_REMOVED or action == FILE_ACTION_RENAMED_NEW_NAME:
                    fileName = struct.unpack("%ds"%(fileNameLen), data[12:(fileNameLen+12)])
                    print(str(fileName[0], "utf-16"))
                elif action == FILE_ACTION_RENAMED_OLD_NAME:
                    fileNameNew = struct.unpack("%ds"%(fileNameLen), data[12:(fileNameLen+12)])
                    print(str(fileNameNew[0], "utf-16"))
                
                if callback:
                    callback(fileName, action, fileNameNew)

                if nextOffset == 0:
                    break
                data = data[nextOffset:]

    def abort(self):
        self._KERNEL32.CloseHandle(self.hDir)

def onFileChanged(fileName, action, fileNameNew=None):
    pass

if __name__ == "__main__":
    try:
        watcher = DirWatcher()
        watcher.start("K:\\t1", onFileChanged)
    except Exception as e:
        print(e)
    finally:
        time.sleep(5)