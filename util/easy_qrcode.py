import sys
import os
import importlib
import subprocess

def checkEnv():
    if sys.maxsize < (1<<31):
        raise Exception('require python x64')
    moduleinfos = [
        #[import-name, package-name-version]
        ['pyzbar', 'pyzbar'],
        ['qrcode', 'qrcode'],
        ['win32api', 'pywin32'],
        ['win32gui', 'pywin32']
        ]
    
    for mi in moduleinfos:
        m, p = mi
        try:
            importlib.import_module(m)
            print(f'import module [{m}]')
        except ImportError:
            print(f'install module [{m}]...')
            subprocess.check_call([f'{sys.executable}', '-m', 'pip', 'install',
                                  p, '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'])


checkEnv()

import pyzbar.pyzbar
import qrcode
from PIL import Image
import win32api
import win32gui

from ctypes import *
from ctypes.wintypes import *
'''
typedef struct tagBITMAPFILEHEADER {
        WORD    bfType;
        DWORD   bfSize;
        WORD    bfReserved1;
        WORD    bfReserved2;
        DWORD   bfOffBits;
} BITMAPFILEHEADER, FAR *LPBITMAPFILEHEADER, *PBITMAPFILEHEADER;
'''
class BITMAPFILEHEADER(Structure):
    _pack_ = 1
    _fields_ = [
        ("bfType", c_char*2),
        ("bfSize", DWORD),
        ("bfReserved1", WORD),
        ("bfReserved2", WORD),
        ("bfOffBits", DWORD),
    ]
'''
typedef struct tagBITMAPINFOHEADER{
        DWORD      biSize;
        LONG       biWidth;
        LONG       biHeight;
        WORD       biPlanes;
        WORD       biBitCount;
        DWORD      biCompression;
        DWORD      biSizeImage;
        LONG       biXPelsPerMeter;
        LONG       biYPelsPerMeter;
        DWORD      biClrUsed;
        DWORD      biClrImportant;
} BITMAPINFOHEADER, FAR *LPBITMAPINFOHEADER, *PBITMAPINFOHEADER;
'''
class BITMAPINFOHEADER(Structure):
    _pack_ = 1
    _fields_ = [
        ("biSize", DWORD),
        ("biWidth", LONG),
        ("biHeight", LONG),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", LONG),
        ("biYPelsPerMeter", LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD),
    ]

def dc2bmp(srcdc, bmp, srcy, srch, dstw, dsth)->bytearray:
    wingdi = WinDLL("gdi32.dll")
    #GetDIBits(memDC, hBmp, 0, szThumb.cy, dst, (BITMAPINFO*)&bmpih, DIB_RGB_COLORS);
    # hdc = HDC(srcdc)
    # hbmp = HBITMAP(bmp)
    bmih = BITMAPINFOHEADER()
    bmih.biSize = sizeof(BITMAPINFOHEADER)
    bmih.biWidth = dstw
    bmih.biHeight = dsth
    bmih.biPlanes = 1
    bmih.biBitCount = 32
    bmih.biCompression = 0
    bmih.biSizeImage = 0
    bmih.biXPelsPerMeter = 0
    bmih.biYPelsPerMeter = 0
    bmih.biClrUsed = 0
    bmih.biClrImportant = 0
    pixel = (BYTE*dstw*dsth*4)()
    ret = wingdi.GetDIBits(srcdc, bmp.handle, srcy, srch, pointer(pixel), pointer(bmih), 0)
    
    bmpfh = BITMAPFILEHEADER()
    bmpfh.bfType = 'BM'.encode()
    bmpfh.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER)
    bmpfh.bfSize = bmpfh.bfOffBits + len(pixel)
    
    return  bytearray(bmpfh) + bytearray(bmih) + bytearray(pixel)

def screencap():
    dc = win32gui.CreateDC("DISPLAY", None, None)
    mons = win32api.EnumDisplayMonitors(None, None)
    x,y,w,h=0,0,0,0
    for mon in mons:
        w0=mon[2][2]-mon[2][0]
        h0=mon[2][3]-mon[2][1]
        x=min(mon[2][0], x)
        y=min(mon[2][1], y)
        w=max(w0, w)
        h=max(h0, h)
    memdc = win32gui.CreateCompatibleDC(dc)
    bmp = win32gui.CreateCompatibleBitmap(dc, w, h)
    oldbmp = win32gui.SelectObject(memdc, bmp)
    #define SRCCOPY (DWORD)0x00CC0020
    win32gui.BitBlt(memdc, 0, 0, w, h, dc, x, y, 0x00CC0020)
    win32gui.SelectObject(memdc, oldbmp)
    bmp = dc2bmp(memdc, bmp, 0, h, w, h)
    
    fn = '.easy-qrcode-screen-cap.bmp'
    if os.path.exists(fn):
        os.remove(fn)
    with open(fn, 'wb') as f:
        f.write(bmp)
    return fn

def decode(img: str):
    res = pyzbar.pyzbar.decode(Image.open(img))
    if not res:
        print(f'no qrcode dectect in current screen')
        return
    for qr in res:
        print(f'{qr.data} @ {qr.rect}')

def encode(url: str, imgpath: str):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    qr.make_image().save(imgpath)
    print(f"save: {imgpath}")

def main():
    cmd = sys.argv[1].lower()
    if cmd == '-i':
        decode(sys.argv[2])
    elif cmd == '-s':
        try:
            fn = screencap()
            decode(fn)
        finally:
            if os.path.exists(fn):
                os.remove(fn)
    elif cmd == '-e':
        encode(sys.argv[2], sys.argv[3])

def usage():
    print("Usage:")
    print("scan image file: easy_qrcode -i \"path_of_qrcode_image\"")
    print("scan current screen: easy_qrcode -s")
    print("encode: easy_qrcode -e \"any_string\" \"path_to_save_qrcode\"")


if __name__ == '__main__':
    main()
