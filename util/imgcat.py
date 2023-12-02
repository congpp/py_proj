import sys
import os
import numpy 
from PIL import Image

def cat(imagePaths: tuple, saveFile: str, isVertical: bool = False):
    img_array = ''
    img = ''
    for i, v in enumerate(imagePaths):
        if i == 0:
            img = Image.open(v)  # 打开图片
            img_array = numpy.array(img)  # 转化为np array对象
        else:
            img_array2 = numpy.array(Image.open(v))
            #1 = 横向拼接
            img_array = numpy.concatenate((img_array, img_array2), axis= 0 if isVertical else 1 )
            img = Image.fromarray(img_array)
 
    # 保存图片
    img.save(saveFile)

def main():
    paths = []
    saveFile=''
    isVertical = False
    argc = len(sys.argv)
    i = 1
    while i < argc:
        v = sys.argv[i]
        print(v)
        if v == '-o':
            saveFile = sys.argv[i+1]
        elif v == '-v':
            isVertical = True
        elif v == '-h':
            isVertical = False
        elif os.path.exists(v):
            paths.append(v)
        i += 1
        
    cat(paths, saveFile)


def usage():
    print("Usage: imgcat all-image-paths -o savefile [-v] [-h]")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        usage()
