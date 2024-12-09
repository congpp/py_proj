# -*- coding: UTF-8 -*-

import win32file
import win32event
import pywintypes
import threading

class DirWatcher:
    def __init__(self) -> None:
        self.overlap = pywintypes.OVERLAPPED()
        self.overlap.hEvent = win32event.CreateEvent(None, False, False, None)
        self.abort = False

    def start(self, dirpath: str, onFileChanged = None):
        self.dirpath = dirpath
        self.onFileChanged = onFileChanged
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        return self

    def _run(self):
        hDir = win32file.CreateFile(self.dirpath,
                                    win32file.GENERIC_READ|0x01, 
                                    win32file.FILE_SHARE_READ|win32file.FILE_SHARE_WRITE|win32file.FILE_SHARE_DELETE, 
                                    None,
                                    win32file.OPEN_EXISTING,
                                    win32file.FILE_FLAG_BACKUP_SEMANTICS | win32file.FILE_FLAG_OVERLAPPED,
                                    None)        
        buf = win32file.AllocateReadBuffer(2048)
        changes = []
        while True:
            win32file.ReadDirectoryChangesW(hDir, buf, True, 0x0D, self.overlap)
            ret = win32event.WaitForSingleObject(self.overlap.hEvent, 1000)
            if ret == win32event.WAIT_OBJECT_0:
                if self.abort:
                    break
                win32file.GetOverlappedResult(hDir, self.overlap, True)
                changes.extend(win32file.FILE_NOTIFY_INFORMATION(buf, len(buf)))
            elif ret == win32event.WAIT_TIMEOUT:
                if changes:
                    print(changes)
                    if self.onFileChanged:
                        self.onFileChanged(changes)
                    changes.clear()
            else:
                break
        win32file.CloseHandle(hDir)
        
    def stop(self):
        self.abort = True
        win32event.SetEvent(self.overlap.hEvent)

if __name__ == "__main__":
    DirWatcher().start("i:\\code", None)