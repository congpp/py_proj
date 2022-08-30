# -*- coding: UTF-8 -*-
import NtProcess
import time

if __name__ == '__main__':
    #obj = ProcessUtil.ProcessSuspend('notepad.exe')
    #time.sleep(5)
    #ProcessUtil.ProcessTerminte('explorer.exe')
    pm = NtProcess.ProcessMonitor()
    proc = pm.getProcessEntries()
    for p in proc:
        print "%08x\t%s" % ( int(p.th32ProcessID), str(p.szExeFile) )

    thrd = pm.getProcessThread('notepad.exe')
    for t in thrd:
        print '%08x\t%08x' % (int(t.th32ThreadID), int(t.th32OwnerProcessID))
