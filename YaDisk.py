#!/usr/bin/python
#coding: utf-8
import requests
import time
from lxml import etree
from YaDiskSettings import LOGIN, PASSWORD


class YaDiskException(Exception):
    pass


class YaDiskXML(object):
    namespaces = {'d': "DAV:"}

    def find(self, node, path):
        return node.find(path, namespaces=self.namespaces)

    def xpath(self, node, path):
        return node.xpath(path, namespaces=self.namespaces)


class YaDisk(object):
    login = None
    password = None
    url = "https://webdav.yandex.ru"
    
    def __init__(self, login, password):
        super(YaDisk, self).__init__()
        self.login = login
        self.password = password

    def sendRequest(self, type, url, headers, data=None):
        req = requests.Request(type, url, headers=headers, auth=(self.login, self.password), data=data)
        with requests.Session() as s:
            return s.send(req.prepare())

    def ls(self, path, offset=None, amount=None):
        def parseContent(content):
            result = []
            tree = etree.XML(content)
            xml = YaDiskXML()
            for response in xml.xpath(tree, "d:response"):
                node = {
                    'path': xml.find(response, "d:href").text,
                    'creationdate': xml.find(response, "d:propstat/d:prop/d:creationdate").text,
                    'displayname': xml.find(response, "d:propstat/d:prop/d:displayname").text,
                    'length': xml.find(response, "d:propstat/d:prop/d:getcontentlength").text,
                    'lastmodified': xml.find(response, "d:propstat/d:prop/d:getlastmodified").text,
                    'isDir': xml.find(response, "d:propstat/d:prop/d:resourcetype/d:collection") != None
                }
                result.append(node)
            return result

        headers = {'Accept': '*/*', 'Depth': 1}
        url = self.url + path
        if (offset != None) and (amount != None):
            url += "?offset=%d&amount=%d" % (offset, amount)
        resp = self.sendRequest("PROPFIND", url, headers)
        if resp.status_code == 207:
            return parseContent(resp.content)
        else:
            raise YaDiskException("Status code is %d" % resp.status_code)

    def df(self):
        def parseContent(content):
            tree = etree.XML(content)
            xml = YaDiskXML()
            node = xml.xpath(tree, "//d:prop")[0]
            return {
                'available': xml.find(node, "d:quota-available-bytes").text, 
                'used': xml.find(node, "d:quota-used-bytes").text
            }

        headers = {'Accept': '*/*', 'Depth': 0}
        data = """
<D:propfind xmlns:D="DAV:">
  <D:prop>
    <D:quota-available-bytes/>
    <D:quota-used-bytes/>
  </D:prop>
</D:propfind>
        """
        resp = self.sendRequest("PROPFIND", self.url, headers, data)
        if resp.status_code == 207:
            return parseContent(resp.content)
        else:
            raise YaDiskException("Status code is %d" % resp.status_code)


if __name__ == "__main__":
    disk = YaDisk(LOGIN, PASSWORD)
    print disk.ls("/")
    print disk.df()