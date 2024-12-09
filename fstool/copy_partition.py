import sys
import os
import uuid


def copy_partition(partitionPath: str, saveFile: str):
    if not partitionPath.startswith('\\\\.\\'):
        partitionPath = '\\\\.\\' + partitionPath[0] + ':'
    fpIn = open(partitionPath, 'rb')
    fpOut = open(saveFile, 'wb')
    while True:
        buf = fpIn.read(1<<20)
        if not buf:
            break
        fpOut.write(buf)
    fpIn.close()
    fpOut.close()


if __name__ == "__main__":
    copy_partition(sys.argv[1], sys.argv[2])
