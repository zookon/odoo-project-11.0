# coding: utf-8


import types
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from base64 import b64encode, b64decode
from urllib import parse


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, str):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                return ' '.join([smart_str(arg, encoding, strings_only,
                                           errors) for arg in s])
            return str(s).encode(encoding, errors)
    elif isinstance(s, str):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


"""
 * 除去数组中的空值和签名参数
 * @param  签名参数组
 * return 去掉空值与签名参数后的新签名参数组
"""


def params_filter(params):
    ks = params.keys()
    # ks.sorted()
    ks = sorted(ks)
    newparams = {}
    prestr = ''
    for k in ks:
        v = params[k]
        k = smart_str(k)
        if k not in ('sign', 'sign_type') and v != '':
            newparams[k] = smart_str(v)
            prestr += '%s=%s&' % (k, newparams[k])
    prestr = prestr[:-1]
    return newparams, prestr


"""
 * 把数组所有元素，按照“参数=参数值”的模式用“&”字符拼接成字符串
 * @param $para 需要拼接的数组
 * return 拼接完成以后的字符串
  函数没有用到，先放着
"""


def createLinkstring(values):
    res = ""
    for k, v in values.iteritems():
        res += k + "=" + v + "&"
    res = res[:-1]
    return res


"""
 * 把数组所有元素，按照“参数=参数值”的模式用“&”字符拼接成字符串，并对字符串做urlencode编码
 * @param $para 需要拼接的数组
 * return 拼接完成以后的字符串
"""


def createLinkstringUrlencode(values):
    res = ""
    for k, v in values.iteritems():
        res += k + "=" + parse.urlencode(v) + "&"
    res = res[:-1]
    return res


"""
 * RSA签名
 * @param data 待签名数据
 * @param private_key 商户私钥字符串
 * return 签名结果
"""


def rsaSign(data, private_key):
    key = RSA.importKey(private_key)
    hash_obj = SHA.new(data)
    signer = PKCS1_v1_5.new(key)
    d = b64encode(signer.sign(hash_obj))
    return d


"""
*生成签名结果
*param $para_sort 已排序要签名的数组
* return 签名结果字符串
"""


def buildRequestMysign(values, private_key):
    # 把数组所有元素，按照“参数=参数值”的模式用“&”字符拼接成字符串
    params, prestr = params_filter(values)
    mysign = rsaSign(prestr, private_key) or ''
    return params, mysign


"""
 * RSA验签
 * @param $data 待签名数据
 * @param $public_key 支付宝的公钥字符串
 * @param $sign 要校对的的签名结果
 * return 验证结果
"""


def rsaVerify(data, public_key, sign):
    rsakey = RSA.importKey(public_key)
    res = SHA.new(data)
    verifier = PKCS1_v1_5.new(rsakey)
    return verifier.verify(res, b64decode(sign))
