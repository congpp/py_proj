import struct
'''
Format C Type       Python type     Standard size
x     pad byte      no value 
c     char          bytes           1
b     char          integer         1
B     uchar         integer         1
?     _Bool         bool            1
h     short         integer         2
H     ushort        integer         2
i     int           integer         4
I     uint          integer         4
l     LONG          integer         4
L     ULONG         integer         4
q     INT64         integer         8
Q     UINT64        integer         8
n     ssize_t       integer         4/8
N     size_t        integer         4/8
f     float         float           4
d     double        float           8
s     char[]        bytes 
p     char[]        bytes 
P     void*         integer 
'''
class easypack:
    def __init__(self) -> None:
        self.align='='
        self.vals=[]
    
    def setNative(self):
        self.align='@'
        return self

    def setNativeNoAlignment(self):
        self.align='='
        return self
    
    def setLittleEndian(self):
        self.align='<'
        return self

    def setBigEndian(self):
        self.align='>'
        return self

    def putChar(self, val):
        if isinstance(val, bytes):
            self.vals.append(['c', val[0:1]])
        if isinstance(val, str):
            self.vals.append(['c', val.encode()[0:1]])
        else:
            raise Exception('required bytes/str')
        return self
        
    def putUChar(self, val):
        self.vals.append(['B', int(val)])
        return self
        
    def putShort(self, val):
        self.vals.append(['h', int(val)])
        return self
        
    def putUShort(self, val):
        self.vals.append(['H', int(val)])
        return self
        
    def putInt(self, val):
        self.vals.append(['i', int(val)])
        return self
        
    def putUInt(self, val):
        self.vals.append(['I', int(val)])
        return self
        
    def putInt64(self, val):
        self.vals.append(['q', int(val)])
        return self
        
    def putUInt64(self, val):
        self.vals.append(['Q', int(val)])
        return self
        
    def putFloat(self, val):
        self.vals.append(['f', float(val)])
        return self
        
    def putDouble(self, val):
        self.vals.append(['d', float(val)])
        return self
        
    def putString(self, val):
        b = str(val).encode()
        self.vals.append(['%ds'%(len(b)), b])
        return self
        
    def get(self)->bytes:
        k, v = self.align, []
        for val in self.vals:
            k += val[0]
            v.append(val[1])
        return struct.pack(k, *v)

class easyunpack:
    def __init__(self) -> None:
        self.align='='
        self.keys=[]
    
    def setNative(self):
        self.align='@'
        return self

    def setNativeNoAlignment(self):
        self.align='='
        return self
    
    def setLittleEndian(self):
        self.align='<'
        return self

    def setBigEndian(self):
        self.align='>'
        return self

    def putChar(self):
        self.keys.append('c')
        return self
        
    def putUChar(self):
        self.keys.append('B')
        return self
        
    def putShort(self):
        self.keys.append('h')
        return self
        
    def putUShort(self):
        self.keys.append('H')
        return self
        
    def putInt(self):
        self.keys.append('i')
        return self
        
    def putUInt(self):
        self.keys.append('I')
        return self
        
    def putInt64(self):
        self.keys.append('q')
        return self
        
    def putUInt64(self):
        self.keys.append('Q')
        return self
        
    def putFloat(self):
        self.keys.append('f')
        return self
        
    def putDouble(self):
        self.keys.append('d')
        return self
        
    def putString(self, len):
        self.keys.append('%ds'%(len))
        return self
        
    def get(self, buf)->tuple:
        k = self.align
        k += ''.join(self.keys)
        return struct.unpack(k, buf)

if __name__ == '__main__':
    b = easypack()\
        .setNativeNoAlignment()\
        .putChar('\x01')\
        .putUChar(2)\
        .putShort(3)\
        .putUShort(4)\
        .putInt(5)\
        .putUInt(6)\
        .putInt64(7)\
        .putUInt64(8)\
        .putFloat(9)\
        .putDouble(10)\
        .putString('11')\
        .get()
    print(b)
    t = easyunpack().setNativeNoAlignment()\
        .putChar()\
        .putUChar()\
        .putShort()\
        .putUShort()\
        .putInt()\
        .putUInt()\
        .putInt64()\
        .putUInt64()\
        .putFloat()\
        .putDouble()\
        .putString(2)\
        .get(b)
    print(t)