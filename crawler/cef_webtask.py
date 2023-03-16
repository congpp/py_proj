# -*- coding: UTF-8 -*-
import json
import os
from cefpython3 import cefpython as cef
import platform
import sys
import tempfile
import hashlib
import mimetypes
import threading
import wevmime
from wevwnd import MsgHandler, MsgSender, WndMsg

ENABLE_LOG = True


def MakeLog(info):
    if ENABLE_LOG:
        print(info)


def UrlToFileName(url: str, mineType: str = None):
    sha1 = hashlib.sha1()
    sha1.update(bytes(url, 'utf-8'))
    filename = sha1.hexdigest()
    ext = None
    srcfile = url.split('?')[0].split('/')[-1]
    if '.' in srcfile:
        ext = '.' + srcfile.split('.')[-1]
    if not ext and mineType:
        ext = mimetypes.guess_extension(mineType)
    if not ext:
        return filename
    return filename + ext


def CheckCefVersion():
    ver = cef.GetVersion()
    MakeLog('[cef info] CEF Python {ver}'.format(ver=ver['version']))
    MakeLog('[cef info] Chromium {ver}'.format(
        ver=ver['chrome_version']))
    MakeLog('[cef info] CEF {ver}'.format(ver=ver['cef_version']))
    MakeLog('[cef info] Python {ver} {arch}'.format(
        ver=platform.python_version(),
        arch=platform.architecture()[0]))
    assert cef.__version__ >= '57.0', 'CEF Python v57.0+ required to run this'

class HtmlVisitor:
    def __init__(self, clientHandler) -> None:
        self._clientHandler = clientHandler

    # StringVisitor.Visit
    def Visit(self, value):
        self._clientHandler._AddMainHtml(value)
        return True

class ClientHandler(object):

    def __init__(self, url: str, msgSender: MsgSender) -> None:
        self._url = url
        self._msgSender = msgSender
        self._resourceHandlers = {}
        sha1 = hashlib.sha1()
        sha1.update(bytes(url, 'utf-8'))
        dirname = sha1.hexdigest()
        self._workingdir = os.path.join(tempfile.gettempdir(), dirname)
        if not os.path.exists(self._workingdir):
            os.mkdir(self._workingdir)
        # index.json
        self._configFile = os.path.join(self._workingdir, 'index.json')
        self._config = {'url': url, 'resources': []}
        MakeLog('new proj: ' + self._configFile)

    def __getitem__(self, key):
        return getattr(self, key)

    def _AddResource(self, webrequest: cef.WebRequest, data: bytearray):
        MakeLog('_AddResource')
        request = webrequest.GetRequest()
        response = webrequest.GetResponse()
        url = request.GetUrl()
        header = request.GetHeaderMap()
        filename = UrlToFileName(url, response.GetMimeType())
        with open(os.path.join(self._workingdir, filename), 'wb') as f:
            f.write(data)
        res = {'url': url,
               'header': json.dumps(header, indent=2),
               'status': response.GetStatus(),
               'mimetype': response.GetMimeType(),
               'group': wevmime.getMimetypeGroup(response.GetMimeType().lower()),
               'size': len(data),
               'cachefile': filename}
        self._config['resources'].append(res)
        # send msg to wnd
        self._msgSender.SendMsg('addresouce', res)

    def _AddMainHtml(self, html: str):
        data = bytes(html, encoding='utf-8')
        filename = self._url.split('?')[0].split('/')[-1]
        if len(filename) == 0:
            filename = 'index.html'
        with open(os.path.join(self._workingdir, filename), 'wb') as f:
            f.write(data)            
        self._config['index'] = filename
        res = {'url': self._url,
               'header': '',
               'status': '',
               'mimetype': mimetypes.guess_type(self._url)[0],
               'size': len(data),
               'cachefile': filename}
        self._config['resources'].append(res)
        # send msg to wnd
        self._msgSender.SendMsg('addresouce', res)
        # save
        self._SaveConfig()
        self._msgSender.SendMsg('onloadend', {'configfile': self._configFile})

    def _SaveConfig(self):
        with open(self._configFile, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent='  ')

    # LoadHandler.OnLoadStart
    def OnLoadStart(self, browser, **_):
        MakeLog('OnLoadStart')
        browser.ExecuteJavascript("""
        window.onload = function(){
            ClientHandler_OnDomReady()
        };
        """)
        self._browser = browser

    def _OnDomReady(self):
        MakeLog('OnDomReady')
        self._htmlVisitor = HtmlVisitor(self)
        self._browser.GetMainFrame().GetSource(self._htmlVisitor)

    # RequestHandler.GetResourceHandler()
    def GetResourceHandler(self, browser, frame, request):
        # Called on the IO thread before a resource is loaded.
        # To allow the resource to load normally return None.
        resHandler = ResourceHandler(self, browser, frame, request)
        self._AddStrongReference(resHandler)
        return resHandler

    # A strong reference to ResourceHandler must be kept
    # during the request. Some helper functions for that.
    # 1. Add reference in GetResourceHandler()
    # 2. Release reference in ResourceHandler.ReadResponse()
    #    after request is completed.
    def _AddStrongReference(self, resHandler):
        self._resourceHandlers[resHandler._resourceHandlerId] = resHandler

    def _ReleaseStrongReference(self, resHandler):
        if resHandler._resourceHandlerId in self._resourceHandlers:
            del self._resourceHandlers[resHandler._resourceHandlerId]
        else:
            MakeLog('_ReleaseStrongReference() FAILED: resource handler '
                    'not found, id = %s' % (resHandler._resourceHandlerId))

    def OnBeforePopup(self, browser, frame, target_url, target_frame_name,
                      target_disposition, user_gesture, popup_features,
                      window_info_out, client, browser_settings_out,
                      no_javascript_access_out):
        wods = {cef.WOD_NEW_FOREGROUND_TAB,
                cef.WOD_NEW_BACKGROUND_TAB,
                cef.WOD_NEW_POPUP,
                cef.WOD_NEW_WINDOW,
                }
        if target_disposition in wods:
            browser.GetMainFrame().LoadUrl(target_url)
            return True
        return False

class ResourceHandler:
    _OBJ_ID = 0

    def __init__(self, clientHandler, browser, frame, request) -> None:
        self._clientHandler = clientHandler
        self._browser = browser
        self._frame = frame
        self._request = request
        self._responseHeadersReadyCallback = None
        self._webRequest = None
        self._webRequestClient = None
        self._offsetRead = 0
        self._cookie = dict()
        ResourceHandler._OBJ_ID += 1
        self._resourceHandlerId = ResourceHandler._OBJ_ID
        MakeLog('new ResourceHandler [%s]' % request.GetUrl())

    def ProcessRequest(self, request, callback):
        # 1. Start the request using WebRequest
        # 2. Return True to handle the request
        # 3. Once response headers are ready call
        #    callback.Continue()
        self._responseHeadersReadyCallback = callback
        self._webRequestClient = WebRequestClient(self)
        # Need to set AllowCacheCredentials and AllowCookies for
        # the cookies to work during POST requests (Issue 127).
        # To skip cache set the SkipCache request flag.
        request.SetFlags(cef.Request.Flags['AllowCachedCredentials']
                         | cef.Request.Flags['AllowCookies']
                         | cef.Request.Flags['SkipCache'])
        # A strong reference to the WebRequest object must kept.
        self._webRequest = cef.WebRequest.Create(
            request, self._webRequestClient)
        MakeLog('new Request [%s]' % (request.GetUrl()))
        return True

    def GetResponseHeaders(self, response, responseLengthOut, redirectUrlOut):
        MakeLog('Get ResponseHeaders [%s]' % (self._request.GetUrl()))
        # 1. If the response length is not known set
        #    responseLengthOut[0] to -1 and ReadResponse()
        #    will be called until it returns False.
        # 2. If the response length is known set
        #    responseLengthOut[0] to a positive value
        #    and ReadResponse() will be called until it
        #    returns False or the specified number of bytes
        #    have been read.
        # 3. Use the |response| object to set the mime type,
        #    http status code and other optional header values.
        # 4. To redirect the request to a new URL set
        #    redirectUrlOut[0] to the new url.
        assert self._webRequestClient._webRequest, 'Response object empty'
        wrcResponse = self._webRequestClient._webRequest.GetResponse()
        response.SetStatus(wrcResponse.GetStatus())
        response.SetStatusText(wrcResponse.GetStatusText())
        response.SetMimeType(wrcResponse.GetMimeType())
        response.SetHeaderMap(wrcResponse.GetHeaderMap())
        if wrcResponse.GetHeaderMultimap():
            response.SetHeaderMultimap(wrcResponse.GetHeaderMultimap())
        responseLengthOut[0] = self._webRequestClient._dataLength
        if not responseLengthOut[0]:
            # Probably a cached page? Or a redirect?
            pass

    def ReadResponse(self, data_out, bytes_to_read, bytes_read_out, callback):
        MakeLog('Read Response [%s]' % (self._request.GetUrl()))
        # 1. If data is available immediately copy up to
        #    bytes_to_read bytes into data_out[0], set
        #    bytes_read_out[0] to the number of bytes copied,
        #    and return true.
        # 2. To read the data at a later time set
        #    bytes_read_out[0] to 0, return true and call
        #    callback.Continue() when the data is available.
        # 3. To indicate response completion return false.
        if self._offsetRead < self._webRequestClient._dataLength:
            dataChunk = bytes(self._webRequestClient._data[self._offsetRead: min(
                self._webRequestClient._dataLength, self._offsetRead + bytes_to_read)])
            data_out[0] = dataChunk
            bytes_read_out[0] = len(dataChunk)
            self._offsetRead += len(dataChunk)
            return True

        self._clientHandler._ReleaseStrongReference(self)
        return False

    def CanGetCookie(self, cookie):
        # Return true if the specified cookie can be sent
        # with the request or false otherwise. If false
        # is returned for any cookie then no cookies will
        # be sent with the request.
        MakeLog("Name=" + cookie.GetName())
        MakeLog("Value=" + cookie.GetValue())
        self._cookie[cookie.GetName()] = cookie.GetValue()
        return True

    def CanSetCookie(self, cookie):
        # Return true if the specified cookie returned
        # with the response can be set or false otherwise.
        return True

    def Cancel(self):
        # Request processing has been canceled.
        pass

class WebRequestClient:
    def __init__(self, resourceHandler: ResourceHandler) -> None:
        self._data = bytearray()
        self._resourceHandler = resourceHandler
        self._dataLength = 0

    def OnUploadProgress(self, web_request, current, total):
        pass

    def OnDownloadProgress(self, web_request, current, total):
        pass

    def OnDownloadData(self, web_request, data):
        # To save data or else
        self._data += data
        self._dataLength += len(data)

    def OnRequestComplete(self, web_request):
        # Are web_request.GetRequest() and
        # self._resourceHandler._request the same? What if
        # there was a redirect, what will GetUrl() return
        # for both of them?
        self._webRequest = web_request

        # save all data
        self._resourceHandler._clientHandler._AddResource(
            self._webRequest, self._data)

        # ResourceHandler.GetResponseHeaders() will get called
        # after _responseHeadersReadyCallback.Continue() is called.
        self._resourceHandler._responseHeadersReadyCallback.Continue()

class GlobalLifeSpandHander: 
    def __init__(self, msgSender: MsgSender) -> None:
        self._msgSender = msgSender  

    def OnAfterCreated(self, browser):
        hWnd = int(browser.GetWindowHandle())
        MakeLog('_OnAfterCreated [%x]' % (hWnd))
        self._msgSender.SendMsg("AfterCreated", {"hwnd": hWnd})

class CefWebTask:

    def __init__(self, msgSender: MsgSender) -> None:
        self._msgSender = msgSender

    def runCef(self, url: str, title: str = None):
        CheckCefVersion()
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        cef.Initialize(settings={
            # 'single_process': True,
            'net_security_expiration_enabled': False,
            'downloads_enabled': False,
            'context_menu': {
                'enabled': True,
                'navigation': True,
                'print': False,
                'view_source': False,
                'external_browser': False,
                'devtools': True,
            }})
        
        lifeSpandHandler = GlobalLifeSpandHander(self._msgSender)
        cef.SetGlobalClientHandler(lifeSpandHandler)

        window_info = cef.WindowInfo()
        # if hParentWnd != None:
        #     window_info.SetAsChild(hParentWnd)
        browser = cef.CreateBrowserSync(
            window_info=window_info, url=url, window_title='Hello World!')
        clientHandler = ClientHandler(url, self._msgSender)

        # Bind js.ClientHandler_OnDomReady to clientHandler._OnDomReady
        browser.SetClientHandler(clientHandler)
        bindings = cef.JavascriptBindings()
        bindings.SetFunction("ClientHandler_OnDomReady",
                             clientHandler["_OnDomReady"])
        browser.SetJavascriptBindings(bindings)

        cef.MessageLoop()
        cef.Shutdown()

    def openWebPage(self, url: str, timeout: int = 30) -> None:
        self.cefThread = threading.Thread(
            target=self.runCef, args=(url, ''))
        self.cefThread.start()

    def closeWebPage(self):
        cef.PostTask(cef.TID_UI, lambda: cef.QuitMessageLoop())
        if self.cefThread:
            self.cefThread.join()
            self.cefThread = None


class CefWebTaskMsgHandler(MsgHandler):
    def __init__(self, wt: CefWebTask) -> None:
        self.wt = wt
        self.handlers = dict()
        self.handlers['openwebpage'] = self.onOpenWebPage
        self.handlers['closewebpage'] = self.onCloseWebPage

    def onOpenWebPage(self, data: dict):
        print('webtask open webpage: ' + data['url'])
        self.wt.openWebPage(url=data['url'])

    def onCloseWebPage(self):
        self.wt.closeWebPage()

    def handleMsg(self, msg: str, data: dict) -> dict:
        if msg not in self.handlers:
            return None
        self.handlers[msg](data)


if __name__ == '__main__':
    class NullMsgSender(MsgSender):
        def SendMsg(self, msg: str, data: dict) -> int:
            print(msg)
            return 0
    msgSender = NullMsgSender()
    url = 'http://192.168.1.198:9001/%E5%BC%80%E5%8F%91%E9%83%A8/%E9%99%88%E8%AF%92%E8%81%AA/Test/'
    wt = CefWebTask(msgSender)
    wt.openWebPage(url=url)
