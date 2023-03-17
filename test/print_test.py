import time

def printR(str):
    print('\033[0;31;40m%s\033[0m' % (str))
def printG(str):
    print('\033[0;32;40m%s\033[0m' % (str))
def printB(str):
    print('\033[0;34;40m%s\033[0m' % (str))
def printY(str):
    print('\033[0;33;40m%s\033[0m' % (str))
def printLoading(timeout = 1.0, interval = 0.2):
    ch = ('— ', '\\ ', '| ', '/ ')
    i, t = 0, time.time()
    while time.time() - t < timeout:
        print('\r'+(ch[i%len(ch)] * 5), end='', flush=True)
        i += 1
        time.sleep(interval)
    print('\r     ')
    print('yes')



if __name__ == '__main__':
    printR('RED')
    printG('GREEN')
    printB('BLUE')
    printY('YELLOW')
    printLoading(2)