# coding: utf-8
#
# 谷歌翻译爬虫
#
import requests
import re
import sys
import time
import json5
import json
import os
import codecs
from urllib import parse
import hashlib

LANGUAGES = {"af": "布尔语(南非荷兰语)", "ak": "契维语", "am": "阿姆哈拉语", "ar": "阿拉伯语", "as": "阿萨姆语", "ay": "艾马拉语", "az": "阿塞拜疆语",
             "be": "白俄罗斯语", "bg": "保加利亚语", "bho": "博杰普尔语", "bm": "班巴拉语", "bn": "孟加拉语", "bs": "波斯尼亚语",
             "ca": "加泰罗尼亚语", "ceb": "宿务语", "ckb": "库尔德语（索拉尼）", "co": "科西嘉语", "cs": "捷克语", "cy": "威尔士语",
             "da": "丹麦语", "de": "德语", "doi": "多格来语", "dv": "迪维希语",
             "ee": "埃维语", "el": "希腊语", "en": "英语", "eo": "世界语", "es": "西班牙语", "et": "爱沙尼亚语", "eu": "巴斯克语",
             "fa": "波斯语", "fi": "芬兰语", "fr": "法语", "fy": "弗里西语",
             "ga": "爱尔兰语", "gd": "苏格兰盖尔语", "gl": "加利西亚语", "gn": "瓜拉尼语", "gom": "贡根语", "gu": "古吉拉特语",
             "ha": "豪萨语", "haw": "夏威夷语", "hi": "印地语", "hmn": "苗语", "hr": "克罗地亚语", "ht": "海地克里奥尔语", "hu": "匈牙利语", "hy": "亚美尼亚语",
             "id": "印尼语", "ig": "伊博语", "ilo": "伊洛卡诺语", "is": "冰岛语", "it": "意大利语", "iw": "希伯来语",
             "ja": "日语", "jw": "印尼爪哇语",
             "ka": "格鲁吉亚语", "kk": "哈萨克语", "km": "高棉语", "kn": "卡纳达语", "ko": "韩语", "kri": "克里奥尔语", "ku": "库尔德语（库尔曼吉语）", "ky": "吉尔吉斯语",
             "la": "拉丁语", "lb": "卢森堡语", "lg": "卢干达语", "ln": "林格拉语", "lo": "老挝语", "lt": "立陶宛语", "lus": "米佐语", "lv": "拉脱维亚语",
             "mai": "迈蒂利语", "mg": "马尔加什语", "mi": "毛利语", "mk": "马其顿语", "ml": "马拉雅拉姆语", "mn": "蒙古语", "mni-Mtei": "梅泰语（曼尼普尔语）", "mr": "马拉地语", "ms": "马来语", "mt": "马耳他语", "my": "缅甸语",
             "ne": "尼泊尔语", "nl": "荷兰语", "no": "挪威语", "nso": "塞佩蒂语", "ny": "齐切瓦语",
             "om": "奥罗莫语", "or": "奥利亚语",
             "pa": "旁遮普语", "pl": "波兰语", "ps": "普什图语", "pt": "葡萄牙语",
             "qu": "克丘亚语",
             "ro": "罗马尼亚语", "ru": "俄语", "rw": "卢旺达语",
             "sa": "梵语", "sd": "信德语", "si": "僧伽罗语", "sk": "斯洛伐克语", "sl": "斯洛文尼亚语", "sm": "萨摩亚语", "sn": "修纳语", "so": "索马里语", "sq": "阿尔巴尼亚语", "sr": "塞尔维亚语", "st": "塞索托语", "su": "印尼巽他语", "sv": "瑞典语", "sw": "斯瓦希里语",
             "ta": "泰米尔语", "te": "泰卢固语", "tg": "塔吉克语", "th": "泰语", "ti": "蒂格尼亚语", "tk": "土库曼语", "tl": "菲律宾语", "tr": "土耳其语", "ts": "宗加语", "tt": "鞑靼语",
             "ug": "维吾尔语", "uk": "乌克兰语", "ur": "乌尔都语", "uz": "乌兹别克语",
             "vi": "越南语",
             "xh": "南非科萨语",
             "yi": "意第绪语", "yo": "约鲁巴语",
             "zh-CN": "中文（简体）", "zh-TW": "中文（繁体）", "zu": "南非祖鲁语",
             }


class GoogleTr():
    def __init__(self, from_language="auto", to_language="auto") -> None:
        for lang in (from_language, to_language):
            if lang not in LANGUAGES:
                print(LANGUAGES)
                raise (Exception('Invald language: ' + self.to_lang))
        self.from_lang = from_language
        self.to_lang = to_language
        pwd = os.path.split(os.path.realpath(__file__))
        self.cache_file = pwd[0] + "/google_tr_cache.json"
        print('cache: ' + self.cache_file)
        try:
            with codecs.open(self.cache_file, 'r', 'utf-8') as fp:
                self.cache = json.load(fp)
                fp.close()
        except:
            self.cache = {}

    def __del__(self):
        with codecs.open(self.cache_file, 'w', 'utf-8') as fp:
            json.dump(self.cache, fp, indent=4, ensure_ascii=False)

    def __getCacheKey__(self, src):
        m = hashlib.md5()
        m.update(src.encode('utf-8'))
        return m.hexdigest()

    def __addCache__(self, src, dst):
        if self.from_lang not in self.cache:
            self.cache[self.from_lang] = {}
        if self.to_lang not in self.cache[self.from_lang]:
            self.cache[self.from_lang][self.to_lang] = {}

        srcMd5 = self.__getCacheKey__(src)
        self.cache[self.from_lang][self.to_lang][srcMd5] = {
            'src': src, 'dst': dst}

    def __translateFromCached__(self, src):
        try:
            srcMd5 = self.__getCacheKey__(src)
            if srcMd5 in self.cache[self.from_lang][self.to_lang]:
                it = self.cache[self.from_lang][self.to_lang][srcMd5]
                print('found in cache: %s->%s' % (it['src'], it['dst']))
                return it['dst']
            return None
        except:
            return None

    def translate(self, text):
        cacheTxt = self.__translateFromCached__(text)
        if cacheTxt != None:
            return cacheTxt
        GOOGLE_TRANSLATE_URL = 'http://translate.google.cn/m?q=%s&tl=%s&sl=%s'
        url = GOOGLE_TRANSLATE_URL % (
            parse.quote(text), self.to_lang, self.from_lang)
        response = requests.get(url)
        data = response.text
        # (?s)=单行，?:=搜索但不存结果
        expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
        result = re.findall(expr, data)
        if (len(result) == 0):
            return None
        self.__addCache__(text, result[0])
        return result[0]

    def translateEx(self, src):
        for i in range(0, 3):
            try:
                dst = self.translate(src)
                if dst != None and len(dst) > 0:
                    return dst
            except Exception:
                pass
            time.sleep(i+1*3)
        return None

    def translageLanguaueJson(self, srcFile, dstDir):
        srcJS = json5.loads(codecs.open(srcFile, 'r', 'utf-8-sig').read())
        if not os.path.exists(dstDir):
            os.mkdir(dstDir)
        dstFile = dstDir + '/' + self.to_lang + '.json'
        if os.path.exists(dstFile):
            os.remove(dstFile)
        dstJS = {}
        if self.to_lang not in LANGUAGES:
            print(LANGUAGES)
            raise (Exception('Invald language: ' + self.to_lang))

        dstJS['language'] = self.to_lang

        dstStr = []
        for strtb in srcJS['strings']:
            src = strtb['text']
            dst = self.translateEx(src)
            dstStr.append({'id': strtb['id'], 'text': dst})
            print('[%s]->[%s]' % (src, dst))

        dstJS['strings'] = dstStr
        with codecs.open(dstFile, 'w', 'utf-8') as fp:
            json.dump(dstJS, fp, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    pwd = os.path.split(os.path.realpath(__file__))
    #srcFile = pwd[0] + r'\..\..\src\Lib\AppRes\res\language\default.json'
    #dstDir = pwd[0]+'/out'
    lang = sys.argv[1]
    srcFile = sys.argv[2]
    dstDir = sys.argv[3]
    if not os.path.exists(srcFile) or not os.path.exists(dstDir):
        raise (Exception("Usage: " + pwd[1] + " lang-key inputfile outputdir"))
    tr = GoogleTr('zh-CN', lang)
    tr.translageLanguaueJson(srcFile, dstDir)
