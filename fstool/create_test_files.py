import sys
import os
import uuid

rootPath = "I:\\"  # sys.argv[1]
maxDepth = 3
maxSubDir = 3
maxSubFile = 16
fileDataSize= 500<<10


def createTestFiles(curPath, dirId: tuple):
    if len(dirId) > maxDepth:
        return
    dirName=''
    for id in dirId:
        dirName += '%d.' % (id)
    dirName=dirName[:-1]
    dirPath = os.path.join(curPath, dirName)
    print(f"create dir: [{dirPath}]")
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    for id in range(maxSubFile):
        fileName = dirName + f".{id}.txt"
        filePath = os.path.join(dirPath, fileName)
        print(f"create file: [{filePath}]")
        with open(filePath, "w") as fp:
            fp.write('TESTDATA')
            fileData = (fileName + "\n")
            fileData = fileData * (fileDataSize//len(fileData))
            fp.write(fileData)
            fp.close()
    for id in range(maxSubDir):
        createTestFiles(dirPath, dirId+[id])
    pass


def main():
    for id in range(maxSubDir):
        createTestFiles(rootPath, [id])


if __name__ == "__main__":
    main()
