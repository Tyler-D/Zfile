#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import urlparse
import urllib2
import urllib
import time
import httplib

import gzip
from io import BytesIO

class HttpClient(object):
    def __init__(self):
        pass

    def get(self, url):
        headers = self.set_headers(url)
        req = urllib2.Request(url=url, headers=headers)

        resp = None
        status = 200

        try:
            resp = urllib2.urlopen(req, timeout=15)
        except urllib2.URLError, e:
            return resp
        except urllib2.HTTPError, e:
            status = e.code
        except httplib.BadStatusLine, e:
            #没有接受到客户端发送的数据
            return resp
        except Exception, e:
            return resp

        if not resp:
            return resp

        if 200 != status:
            return resp

        # 解决乱码
        try:
            is_gzip = resp.headers.get('Content-Encoding')
        except:
            is_gzip = None

        if is_gzip:
            buffer = BytesIO(resp.read())
            gz = gzip.GzipFile(fileobj=buffer)
            data = gz.read()
            gz.close()
            return data

        return resp.read()

    def post(self, url, data):
        headers = self.set_headers(url)
        req = urllib2.Request(url=url, headers=headers,
                data=urllib.urlencode(data))

        resp = None
        status = 200

        try:
            resp = urllib2.urlopen(req, timeout=15)
        except urllib2.URLError, e:
            return resp
        except urllib2.HTTPError, e:
            status = e.code
        except httplib.BadStatusLine, e:
            #没有接受到客户端发送的数据
            return resp
        except Exception, e:
            return resp

        if not resp:
            return resp

        if 200 != status:
            return resp

        return resp.read()

    def set_headers(self, url, **kargs):
        """自定义header,防止被禁,某些情况如豆瓣,还需制定cookies,否则被ban
        使用参数传入可以覆盖默认值，或添加新参数，如cookies
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            #设置Host会导致TooManyRedirects, 因为hostname不会随着原url跳转而更改,可不设置
            'Host': urlparse.urlparse(url).netloc,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0',
            #反盗链
            'Referer': url,
            }

        return headers
