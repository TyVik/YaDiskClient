#!/usr/bin/env python
# coding: utf-8
from warnings import warn

from requests import request
import xml.etree.ElementTree as ET
import sys
import hashlib
import os
import http.client
import logging
import base64

class YaDiskException(Exception):
    """Common exception class for YaDisk. Arg 'code' have code of HTTP Error."""
    code = None

    def __init__(self, code, text):
        super(YaDiskException, self).__init__(text)
        self.code = code

    def __str__(self):
        return "{code}. {message}".format(code=self.code, message=super(YaDiskException, self).__str__())


class YaDiskXML(object):
    namespaces = {'d': "DAV:"}

    def find(self, node, path):
        """Wrapper for lxml`s find."""

        return node.find(path, namespaces=self.namespaces)

    def xpath(self, node, path):
        """Wrapper for lxml`s xpath."""

        return node.xpath(path, namespaces=self.namespaces)


def _check_dst_absolute(dst):
    if dst[0] != '/':
        raise YaDiskException(400, "Destination path must be absolute")


class YaDisk(object):
    """Main object for work with Yandex.disk."""

    login = None
    password = None
    host = "webdav.yandex.ru"
    url = "https://" + host + "/"
    namespaces = {'d': 'DAV:'}
    bufSize = 65536
    maxSizeFile = 50*1024**3 # https://yandex.ru/support/disk/uploading.html
    
    def __init__(self, login, password):
        super(YaDisk, self).__init__()
        self.login = login
        self.password = password
        if self.login is None or self.password is None:
            raise YaDiskException(400, "Please, specify login and password for Yandex.Disk account.")

    def _calcHash(self, file):
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(file, 'rb') as f:
            while True:
                data = f.read(self.bufSize)
                if not data:
                    break
                md5.update(data)
                sha256.update(data)
        return md5.hexdigest(), sha256.hexdigest()

    def _sendRequest(self, type, addUrl="/", addHeaders={}, data=None, runAtContinue = True):
        headers = {"Accept": "*/*"}
        headers.update(addHeaders)
        url = self.url + addUrl
        # https://stackoverflow.com/questions/38084993/python-http-client-stuck-on-100-continue
        if "Expect" not in headers:
            return request(type, url, headers=headers, auth=(self.login, self.password), data=data)
        else:
            # https://yandex.ru/dev/disk/doc/dg/concepts/quickstart-docpage/
            auth = base64.b64encode(bytes(self.login + ':' + self.password, 'utf-8')).decode('utf-8')
            headers.update({ 'Authorization' : 'Basic ' + auth })
            conn = ContinueHTTPSConnection(self.host)
            conn.request(type, url, body=None, headers=headers)
            response = conn.getresponse()
            if (response.status == http.client.CONTINUE) and runAtContinue:
                response.read()
                conn.send(data)
                response = conn.getresponse()
            else:
                conn.close()
            class R:
                status_code = 0
                content = ""
            resp = R()
            resp.status_code = response.status
            resp.content = response.msg
            return resp
           

    def ls(self, path, offset=None, amount=None):
        """
        Return list of files/directories. Each item is a dict. 
        Keys: 'path', 'creationdate', 'displayname', 'length', 'lastmodified', 'isDir'.
        """
        
        def parseContent(content):
            result = []
            root = ET.fromstring(content)
            for response in root.findall('.//d:response', namespaces=self.namespaces):
                node = {
                    'path': response.find("d:href", namespaces=self.namespaces).text,
                    'creationdate': response.find("d:propstat/d:prop/d:creationdate", namespaces=self.namespaces).text,
                    'displayname': response.find("d:propstat/d:prop/d:displayname", namespaces=self.namespaces).text,
                    'lastmodified': response.find("d:propstat/d:prop/d:getlastmodified", namespaces=self.namespaces).text,
                    'isDir': response.find("d:propstat/d:prop/d:resourcetype/d:collection", namespaces=self.namespaces) != None
                }
                if not node['isDir']:
                    node['length'] = response.find("d:propstat/d:prop/d:getcontentlength", namespaces=self.namespaces).text
                    node['etag'] = response.find("d:propstat/d:prop/d:getetag", namespaces=self.namespaces).text
                    node['type'] = response.find("d:propstat/d:prop/d:getcontenttype", namespaces=self.namespaces).text
                result.append(node)
            return result

        url = path
        if (offset is not None) and (amount is not None):
            url += "?offset={offset}&amount={amount}".format(offset=offset, amount=amount)
        resp = self._sendRequest("PROPFIND", url, {'Depth': '1'})
        if resp.status_code == 207:
            return parseContent(resp.content)
        else:
            raise YaDiskException(resp.status_code, resp.content)

    def df(self):
        """Return dict with size of Ya.Disk. Keys: 'available', 'used'."""

        def parseContent(content):
            root = ET.fromstring(content)
            return {
                'available': root.find(".//d:quota-available-bytes", namespaces=self.namespaces).text, 
                'used': root.find(".//d:quota-used-bytes", namespaces=self.namespaces).text
            }

        data = """
<D:propfind xmlns:D="DAV:">
  <D:prop>
    <D:quota-available-bytes/>
    <D:quota-used-bytes/>
  </D:prop>
</D:propfind>
        """
        resp = self._sendRequest("PROPFIND", "/", {'Depth': '0'}, data)
        if resp.status_code == 207:
            return parseContent(resp.content)
        else:
            raise YaDiskException(resp.status_code, resp.content)

    def mkdir(self, path):
        """Create directory. All part of path must be exists. Raise exception when path already exists."""

        resp = self._sendRequest("MKCOL", path)
        if resp.status_code != 201:
            if resp.status_code == 409:
                raise YaDiskException(409, "Part of path {} does not exists".format(path))
            elif resp.status_code == 405:
                raise YaDiskException(405, "Path {} already exists".format(path))
            else:
                raise YaDiskException(resp.status_code, resp.content)

    def rm(self, path):
        """Delete file or directory."""

        resp = self._sendRequest("DELETE", path)
        # By documentation server must return 200 "OK", but I get 204 "No Content".
        # Anyway file or directory have been removed.
        if not (resp.status_code in (200, 204)):
            raise YaDiskException(resp.status_code, resp.content)

    def cp(self, src, dst):
        """Copy file or directory."""

        _check_dst_absolute(dst)
        resp = self._sendRequest("COPY", src, {'Destination': dst})
        if resp.status_code not in (201, 202):
            raise YaDiskException(resp.status_code, resp.content)

    def mv(self, src, dst):
        """Move file or directory."""

        _check_dst_absolute(dst)
        resp = self._sendRequest("MOVE", src, {'Destination': dst})
        if resp.status_code != 201:
            raise YaDiskException(resp.status_code, resp.content)

    def upload(self, file, path, calcHash=True):
        """Upload file."""

        size = os.path.getsize(file)
        if size > self.maxSizeFile:
            print ("Big file. Aborted.")
            return False
        
        if (calcHash):
            md5, sha256 = self._calcHash(file)
            with open(file, "rb") as f:
                resp = self._sendRequest("PUT", path, data=f, addHeaders={
                    "Etag": md5,
                    "Sha256": sha256,
                    "Content-Length": str(size),
                    "Expect": "100-continue"
                    })
        else:
            with open(file, "rb") as f:
                resp = self._sendRequest("PUT", path, data=f)
                
        if resp.status_code != 201:
            raise YaDiskException(resp.status_code, resp.content)
        else:
            return True

    def uploadViaHash(self, md5, sha256, size, path):
        """Upload file via hash."""

        if size > self.maxSizeFile:
            print ("Big file. Aborted.")
            return False
        
        resp = self._sendRequest("PUT", path, runAtContinue = False, addHeaders={
                "Etag": md5,
                "Sha256": sha256,
                "Content-Length": str(size),
                "Expect": "100-continue"
                    })

        if resp.status_code == 201:
            return True
        elif resp.status_code == 100:
            return False
        else:
            raise YaDiskException(resp.status_code, resp.content)

    def download(self, path, file):
        """Download remote file to disk."""

        resp = self._sendRequest("GET", path)
        if resp.status_code == 200:
            with open(file, "wb") as f:
                f.write(resp.content)
        else:
            raise YaDiskException(resp.status_code, resp.content)
            
    def publish(self, path):
        """Publish file or folder and return public url"""
        
        def parseContent(content):
            root = ET.fromstring(content)
            prop = root.find(".//d:prop", namespaces=self.namespaces)
            return prop.find("{urn:yandex:disk:meta}public_url").text.strip()
        
        data = """
<propertyupdate xmlns="DAV:">
  <set>
    <prop>
      <public_url xmlns="urn:yandex:disk:meta">true</public_url>
    </prop>
  </set>
</propertyupdate>
        """
        
        _check_dst_absolute(path)
        resp = self._sendRequest("PROPPATCH", addUrl=path, data=data)
        if resp.status_code == 207:
            return parseContent(resp.content)
        else:
            raise YaDiskException(resp.status_code, resp.content)
    
    def unpublish(self, path):
        """Make public file or folder private (delete public url)"""
        
        data = """
<propertyupdate xmlns="DAV:">
  <remove>
    <prop>
      <public_url xmlns="urn:yandex:disk:meta" />
    </prop>
  </remove>
</propertyupdate>
        """
        
        _check_dst_absolute(path)
        resp = self._sendRequest("PROPPATCH", addUrl=path, data=data)
        if resp.status_code == 207:
            pass
        else:
            raise YaDiskException(resp.status_code, resp.content)

    def publish_doc(self, path):
        warn('This method was deprecated in favor method "publish"', DeprecationWarning, stacklevel=2)
        return self.publish(path)

    def hide_doc(self, path):
        warn('This method was deprecated in favor method "unpublish"', DeprecationWarning, stacklevel=2)
        return self.unpublish(path)


class ContinueHTTPResponse(http.client.HTTPResponse):
    def _read_status(self, *args, **kwargs):
        version, status, reason = super()._read_status(*args, **kwargs)
        if status == 100:
            status = 199
        return version, status, reason

    def begin(self, *args, **kwargs):
        super().begin(*args, **kwargs)
        if self.status == 199:
            self.status = 100

    def _check_close(self, *args, **kwargs):
        return super()._check_close(*args, **kwargs) and self.status != 100


class ContinueHTTPSConnection(http.client.HTTPSConnection):
    response_class = ContinueHTTPResponse

    def getresponse(self, *args, **kwargs):
        logging.debug('running getresponse')
        response = super().getresponse(*args, **kwargs)
        if response.status == 100:
            setattr(self, '_HTTPConnection__state', http.client._CS_REQ_SENT)
            setattr(self, '_HTTPConnection__response', None)
        return response
