# -*- coding: UTF-8 -*-
from ctypes import *
"""
struct DownTaskParam
{
    DownTaskParam()
    {
        memset(this, 0, sizeof(DownTaskParam));
        nReserved1       = 5;
        bReserved            = FALSE;
        DisableAutoRename    = FALSE;
        IsOnlyOriginal       = FALSE;
        IsResume             = TRUE;
    }
    int nReserved;
    wchar_t szTaskUrl[2084];          // 任务URL
    wchar_t szRefUrl[2084];           // 引用页
    wchar_t szCookies[4096];          // 浏览器cookie
    wchar_t szFilename[MAX_PATH];     // 下载保存文件名.
    wchar_t szReserved0[MAX_PATH];
    wchar_t szSavePath[MAX_PATH];     // 文件保存目录
    HWND  hReserved;
    BOOL bReserved; 
    wchar_t szReserved1[64];
    wchar_t szReserved2[64];
    BOOL IsOnlyOriginal;            // 是否只从原始地址下载
    UINT nReserved1;
    BOOL DisableAutoRename;         // 禁止智能命名
    BOOL IsResume;                  // 是否用续传
    DWORD reserved[2048];
};
"""
class DownTaskParam(Structure):
    _pack_ = 1
    _fields_ = [
    ('nReserved', c_int),
    ('szTaskUrl', c_wchar * 2084),        # 任务URL
    ('szRefUrl', c_wchar * 2084),         # 引用页
    ('szCookies', c_wchar * 4096),        # 浏览器cookie
    ('szFilename', c_wchar * 256),        # 下载保存文件名.
    ('szReserved0', c_wchar * 256),
    ('szSavePath',  c_wchar * 256),       # 文件保存目录
    ('hReserved', c_void_p),
    ('bReserved', c_long),
    ('szReserved1', c_wchar * 128),
    ('IsOnlyOriginal', c_long),         # 是否只从原始地址下载
    ('nReserved1', c_uint32),
    ('DisableAutoRename', c_long),      # 禁止智能命名
    ('IsResume', c_long),               # 是否用续传
    ('reserved', c_ulong * 2048),
    ]

    def encode(self):
        return string_at(addressof(self), sizeof(self))

    def decode(self, data):
        memmove(addressof(self), data, sizeof(self))
        return len(data)
"""
struct DownTaskInfo
{
    DownTaskInfo()
    {
        memset(this, 0, sizeof(DownTaskInfo));
        stat        = TSC_PAUSE;
        fail_code   = TASK_ERROR_UNKNOWN;
        fPercent = 0;
        bIsOriginUsable = false;
        fHashPercent = 0;
    }
    DOWN_TASK_STATUS    stat;
    TASK_ERROR_TYPE     fail_code;
    wchar_t     szFilename[MAX_PATH];
    wchar_t     szReserved0[MAX_PATH];
    __int64     nTotalSize;         // 该任务总大小(字节)
    __int64     nTotalDownload;     // 下载有效字节数(可能存在回退的情况)
    float       fPercent;           // 下载进度
    int         nReserved0;
    int         nSrcTotal;          // 总资源数
    int         nSrcUsing;          // 可用资源数
    int         nReserved1;
    int         nReserved2;
    int         nReserved3;
    int         nReserved4;
    __int64     nReserved5;
    __int64     nDonationP2P;       // p2p贡献字节数
    __int64     nReserved6;
    __int64     nDonationOrgin;     // 原始资源共享字节数
    __int64     nDonationP2S;       // 镜像资源共享字节数
    __int64     nReserved7;
    __int64     nReserved8;
    int         nSpeed;             // 即时速度(字节/秒)
    int         nSpeedP2S;          // 即时速度(字节/秒)
    int         nSpeedP2P;          // 即时速度(字节/秒)
    bool        bIsOriginUsable;    // 原始资源是否有效
    float       fHashPercent;       // 现不提供该值
    int         IsCreatingFile;     // 是否正在创建文件
    DWORD       reserved[64];
};
"""

class DownTaskInfo(Structure):
    _pack_ = 1
    _fields_ = [
    ('nStat', c_uint32),
    ('nFailCode', c_uint32),
    ('szFilename', c_wchar * 256),
    ('szReserved0', c_wchar * 256),
    ('nTotalSize', c_longlong),         # 该任务总大小(字节)
    ('nTotalDownload', c_longlong),     # 下载有效字节数(可能存在回退的情况)
    ('fPercent', c_float),           # 下载进度
    ('nReserved0', c_int),
    ('nSrcTotal', c_int),          # 总资源数
    ('nSrcUsing', c_int),          # 可用资源数
    ('nReserved1_4', c_int * 4),
    ('nReserved5', c_longlong),
    ('nDonationP2P', c_longlong),       # p2p贡献字节数
    ('nReserved6', c_longlong),
    ('nDonationOrgin', c_longlong),     # 原始资源共享字节数
    ('nDonationP2S', c_longlong),       # 镜像资源共享字节数
    ('nReserved7_8', c_longlong * 2),
    ('nSpeed', c_int),              # 即时速度(字节/秒)
    ('nSpeedP2S', c_int),           # 即时速度(字节/秒)
    ('nSpeedP2P', c_int),           # 即时速度(字节/秒)
    ('bIsOriginUsable', c_char),     # 原始资源是否有效
    ('fHashPercent', c_float),       # 现不提供该值
    ('IsCreatingFile', c_int),      # 是否正在创建文件
    ('reserved', c_ulong * 64),
    ]

    def encode(self):
        return string_at(addressof(self), sizeof(self))

    def decode(self, data):
        memmove(addressof(self), data, sizeof(self))
        return len(data)

"""
struct DOWN_PROXY_INFO
{
    BOOL        bIEProxy;
    BOOL        bProxy;
    DOWN_PROXY_TYPE stPType;
    DOWN_PROXY_AUTH_TYPE    stAType;
    wchar_t     szHost[2048];
    INT32       nPort;
    wchar_t     szUser[50];
    wchar_t     szPwd[50];
    wchar_t     szDomain[2048];
};
"""
class DOWN_PROXY_INFO(Structure):
    _pack_ = 1
    _fields_ = [
    ('bIEProxy', c_long),
    ('bProxy', c_long),
    ('stPType', c_int),
    ('stAType', c_int),
    ('szHost', c_wchar*2048),
    ('nPort', c_int),
    ('szUser', c_wchar*50),
    ('szPwd', c_wchar*50),
    ('szDomain', c_wchar*2048),
    ]

    def encode(self):
        return string_at(addressof(self), sizeof(self))

    def decode(self, data):
        memmove(addressof(self), data, sizeof(self))
        return len(data)

class XLDL:
    dll = 0

    def __init__(self, strDllPath):
        self.dll = cdll.LoadLibrary(strDllPath)
        self.dll.XL_Init.argtypes =[]
        self.dll.XL_Init.restypes =[c_long]
        self.dll.XL_UnInit.argtypes =[]
        self.dll.XL_UnInit.restypes =[c_long]
        self.dll.XL_CreateTaskByThunder.argtypes = [c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p]
        self.dll.XL_CreateTaskByThunder.restypes = [c_long]
        self.dll.XL_StartTask.argtypes = [c_void_p]
        self.dll.XL_StartTask.restypes = [c_long]
        self.dll.XL_CreateTaskByURL.argtypes = [c_wchar_p,c_wchar_p,c_wchar_p,c_long]
        self.dll.XL_CreateTaskByURL.restypes = [c_void_p]
    
    def Init(self):
        return self.dll.XL_Init();
        
    def UnInit(self):
        return self.dll.XL_UnInit();
        
    def TaskCreate(downTaskParam):
        return 0

    def TaskDelete(self, nTaskID):
        return self.dll.XL_DeleteTask(nTaskID);
        
    def TaskStart(self, nTaskID):
        hTask = c_void_p()
        hTask.value = nTaskID
        return self.dll.XL_StartTask(hTask)
        
    def TaskPause(self, nTaskID):
        return 0
    def TaskQuery(self, nTaskID, downTaskInfo):
        return 0
    def TaskQueryEx(self, nTaskID, downTaskInfo):
        return 0
    def LimitSpeed(self,  nBps):
        return 0
    def LimitUploadSpeed(self,  nTcpBps, nOtherBps):
        return 0
    def DelTempFile(self, downTaskParam):
        return 0
    def SetProxy(self, downPROXYINFO):
        return 0
    def SetUserAgent(self, strUserAgent):
        return 0
    def GetFileSizeWithUrl(self, strURL, iFileSize):
        return 0
    def ParseThunderPrivateUrl(self, strThunderUrl, strNormalUrlBuffer, nBufferLen):
        return 0
    def SetAdditionInfo(self, task_id, pSockInfo, strHttpRespBuf, bBufLen):
        return 0
    def SetFileIdAndSize(self, nTaskID, szFileId, nFileSize):
        return 0

    def ForceStopTask(self, nTaskID):
        return 0

    def CreateTaskByURL(self, strUrl, strPath, strFileName, IsResume):
        pStrUrl = c_wchar_p();
        pStrUrl.value = strUrl;
        pstrPath = c_wchar_p()
        pstrPath.value = strPath.encode('gb2312')
        pstrFileName = c_wchar_p()
        pstrFileName.value = strFileName.encode('gb2312')
        nIsResume = c_long()
        nIsResume.value = IsResume
        return self.dll.XL_CreateTaskByURL(pStrUrl, pstrPath, pstrFileName, nIsResume)

    def CreateTaskByThunder(self, strUrl, strFileName, strReferUrl, strCharSet, strCookie):
        pStrUrl = c_wchar_p()
        pStrUrl.value = strUrl.encode('gb2312')
        pstrFileName = c_wchar_p()
        pstrFileName.value = strFileName.encode('gb2312')
        pstrReferUrl = c_wchar_p()
        pstrReferUrl.value = strReferUrl.encode('gb2312')
        pstrCharSet = c_wchar_p()
        pstrCharSet.value = strCharSet.encode('gb2312')
        pstrCookie = c_wchar_p()
        pstrCookie.value = strCookie.encode('gb2312')
        return self.dll.XL_CreateTaskByThunder(pStrUrl, pstrFileName, pstrReferUrl, pstrCharSet, pstrCookie)

    def TaskStop(self, nTaskID):
        return 0
        
        
    