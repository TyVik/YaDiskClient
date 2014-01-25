#!/usr/bin/python
#coding: utf-8
import requests
import time
from lxml import etree
from YaDiskSettings import LOGIN, PASSWORD


class YaDiskException(Exception):
    pass


class YaDisk(object):
    login = None
    password = None
    url = "https://webdav.yandex.ru"
    
    def __init__(self, login, password):
        super(YaDisk, self).__init__()
        self.login = login
        self.password = password

    def ls(self, path, offset=None, amount=None):
        def parseContent(content):
            result = []
            tree = etree.XML(content)
            for response in tree.xpath("d:response", namespaces={'d': "DAV:"}):
                node = {
                    'path': response.find("d:href", namespaces={'d': "DAV:"}).text,
                    'creationdate': response.find("d:propstat/d:prop/d:creationdate", namespaces={'d': "DAV:"}).text,
                    'displayname': response.find("d:propstat/d:prop/d:displayname", namespaces={'d': "DAV:"}).text,
                    'length': response.find("d:propstat/d:prop/d:getcontentlength", namespaces={'d': "DAV:"}).text,
                    'lastmodified': response.find("d:propstat/d:prop/d:getlastmodified", namespaces={'d': "DAV:"}).text,
                    'isDir': response.find("d:propstat/d:prop/d:resourcetype/d:collection", namespaces={'d': "DAV:"}) != None
                }
                result.append(node)
            return result

        headers = {'Accept': '*/*', 'Depth': 1}
        url = self.url + path
        if (offset != None) and (amount != None):
            url += "?offset=%d&amount=%d" % (offset, amount)
        print url
        req = requests.Request("PROPFIND", url, headers=headers, auth=(self.login, self.password))
        with requests.Session() as s:
            resp = s.send(req.prepare())
            if resp.status_code == 207:
                return parseContent(resp.content)



if __name__ == "__main__":
    disk = YaDisk(LOGIN, PASSWORD)
    print disk.ls("/")