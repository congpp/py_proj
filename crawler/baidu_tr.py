# -*- coding: UTF-8 -*-
import sys
import requests
import re
import execjs


class BaiduTr():
    url = 'https://fanyi.baidu.com/v2transapi?from=zh&to=en'
    
    langList = {
        'af': '南非语', 'am': '阿姆哈拉语', 'ara': '阿拉伯语', 'as': '阿萨姆语', 'az': '阿塞拜疆语',
        'be': '白俄罗斯语', 'bn': '孟加拉语', 'bs': '波斯尼亚语', 'bul': '保加利亚语', 
        'ca': '加泰罗尼亚语', 'cht': '中文繁体', 'cs': '捷克语', 'cy': '威尔士语',
        'dan': '丹麦语', 'de': '德语',
        'el': '希腊语', 'en': '英语', 'eo': '世界语', 'est': '爱沙尼亚语', 'eu': '巴斯克语',
        'fa': '波斯语', 'fin': '芬兰语', 'fra': '法语',
        'ga': '爱尔兰语', 'gl': '加利西亚语', 'gu': '古吉拉特语',
        'ha': '豪萨语', 'hi': '印地语', 'hr': '克罗地亚语', 'hu': '匈牙利语', 'hy': '亚美尼亚语',
        'id': '印尼语', 'ig': '伊博语', 'ir': '伊朗语', 'is': '冰岛语', 'it': '意大利语', 'iu': '因纽特语', 'iw': '希伯来语',
        'jp': '日语', 'jpka': '日语假名',
        'ka': '格鲁吉亚语', 'kk': '哈萨克语', 'kn': '卡纳达语', 'kor': '韩语', 'ky': '吉尔吉斯语',
        'lb': '卢森堡语', 'lt': '立陶宛语', 'lv': '拉脱维亚语',
        'mi': '毛利语', 'mk': '马其顿语', 'mr': '马拉提语', 'ms': '马来语', 'mt': '马耳他语',
        'ne': '尼泊尔语', 'nl': '荷兰语', 'no': '挪威语',
        'or': '奥利亚语',
        'pa': '旁遮普语', 'pl': '波兰语', 'pt_BR': '巴西语', 'pt': '葡萄牙语',
        'qu': '凯楚亚语',
        'rom': '罗马尼亚语', 'ru': '俄语',
        'si': '僧加罗语', 'sk': '斯洛伐克语', 'slo': '斯洛文尼亚语', 'spa': '西班牙语', 'sq': '阿尔巴尼亚语', 'sr': '塞尔维亚语', 'sw': '斯瓦希里语', 'swe': '瑞典语',
        'ta': '泰米尔语', 'te': '泰卢固语', 'th': '泰语', 'tl': '菲律宾语', 'tn': '塞茨瓦纳语', 'tr': '土耳其语', 'tt': '塔塔尔语',
        'uk': '乌克兰语', 'ur': '乌尔都语', 'uz': '乌兹别克语',
        'vie': '越南语',
        'wyw': '文言文',
        'yo': '约鲁巴语', 'yue': '粤语',
        'zh': '中文', 'zu': '祖鲁语',
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
        'referer': 'https://fanyi.baidu.com/?aldtype=16047',
        'origin': 'https://fanyi.baidu.com',
        'cookie': 'BIDUPSID=BCD3E37271C1619126C5D6BBB322DC60; PSTM=1603001744; BAIDUID=BCD3E37271C1619156C43A509CC424FC:FG=1; REALTIME_TRANS_SWITCH=1; HISTORY_SWITCH=1; FANYI_WORD_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; PSINO=2; BA_HECTOR=akag8ha58g0g2437sn1fqce6m0p; H_PS_PSSID=32820_1453_33049_32941_31254_32706_32961_31709; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1604582586,1604729048,1604730231,1604730315; yjs_js_security_passport=272ae2ab3dcd6f77183a297227987af1b1d7705d_1604730483_js; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1604730580; __yjsv5_shitong=1.0_7_fe7cdb4b7cbc4c9c58587ffa98f2a16c6414_300_1604730579568_120.6.104.221_c74b0f32',
    }

    jsSrc = r"""
        var i = "320305.131321201"

        function n(r, o) {
            for (var t = 0; t < o.length - 2; t += 3) {
                var a = o.charAt(t + 2);
                a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
                a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
                r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
            }
            return r
        }

        function e(r) {
            var o = r.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
            if (null === o) {
                var t = r.length;
                t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))
            } else {
                for (var e = r.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/), C = 0, h = e.length, f = []; h > C; C++)
                    "" !== e[C] && f.push.apply(f, a(e[C].split(""))),
                    C !== h - 1 && f.push(o[C]);
                var g = f.length;
                g > 30 && (r = f.slice(0, 10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join(""))
            }
            var u = void 0
            , l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107);
            u = null !== i ? i : (i = window[l] || "") || "";
            for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
                var A = r.charCodeAt(v);
                128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
                S[c++] = A >> 18 | 240,
                S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
                S[c++] = A >> 6 & 63 | 128),
                S[c++] = 63 & A | 128)
            }
            for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
                p += S[b],
                p = n(p, F);
            return p = n(p, D),
            p ^= s,
            0 > p && (p = (2147483647 & p) + 2147483648),
            p %= 1e6,
            p.toString() + "." + (p ^ m)
        }

        //console.log(e("你好"))
    """

    def __init__(self, srcLang, dstLang) -> None:
        for lang in (srcLang, dstLang):
            if lang not in self.langList:
                print(self.langList)
                raise(Exception("bad lang: %s" % (lang)))
        self.srcLang = srcLang
        self.dstLang = dstLang
        self.jsctx = execjs.compile(self.jsSrc)

    def translate(self, src):
        sign = self.jsctx.call('e', src)

        data = {
            'from': '%s' % self.srcLang,
            'to': '%s' % self.dstLang,
            'query': '%s' % src,
            'transtype': 'realtime',
            'simple_means_flag': '3',
            'sign': '%s' % (str(sign)),
            'token': '417277ffd2b32760906329552e7d639c',
            'domain': 'common'
        }

        response = requests.post(self.url, headers=self.headers, data=data)
        result = re.search('"dst":"(.*?)"', response.text)
        dst = result.group(1)
        if dst.find('\\u') != -1:
            dst = result.group(1).encode('utf-8').decode("unicode-escape")
        print("%s -> %s" % (src, dst))
        return dst


def main():
    if len(sys.argv) != 3:
        raise (Exception("Usage: baidu_tr.py srcLang dstLang\ne.g. baidu_tr.py zh en"))
    srcLang = sys.argv[1]
    dstLang = sys.argv[2]
    tr = BaiduTr(srcLang, dstLang)
    while 1:
        trans = input("请输入待翻译文本(-1=Exit)：")
        if trans == '-1':
            break
        tr.translate(trans)


if __name__ == '__main__':
    main()
