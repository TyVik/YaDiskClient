#!/usr/bin/python
#coding: utf-8
import requests
import time
from YaDiskSettings import APP_ID, APP_SECRET, LOGIN, PASSWORD


class YaDiskException(Exception):
    pass


class YaDiskToken(object):
    _token = None
    _expires = None
    _time = None
    _url = "https://oauth.yandex.ru/token"

    def __init__(self, app_id, app_secret, login, password):
        super(YaDiskToken, self).__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        self.login = login
        self.password = password

    def _getToken(self):
        if self.isValid():
            return self._token

        post = {'grant_type': 'password', 'client_id': self.app_id, 'client_secret': self.app_secret, 'username': self.login, 'password': self.password}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        req = requests.post("https://oauth.yandex.ru/token", headers=headers, data=post)
        if req.status_code in [200, 400]:
            data = req.json()
            if req.status_code == 400:
                raise YaDiskException("%s: %s" % (data['error'], data['error_description']))
        else:
            raise YaDiskException("Request status code is %d" % req.status_code)

        self._token = data['access_token']
        self._expires = data['expires_in']
        self._time = time.time()
        return self._token

    def isValid(self):
        return (self._token != None) and (time.time() < self._time + self._expires)

    token = property(_getToken)

class YaDisk(object):
    login = None
    password = None
    app_id = APP_ID
    app_secret = APP_SECRET
    url = "https://webdav.yandex.ru"
    token = None
    
    def __init__(self, login, password):
        super(YaDisk, self).__init__()
        self.login = login
        self.password = password
        self.token = YaDiskToken(self.app_id, self.app_secret, self.login, self.password)

    def ls(self, path):
        headers = {'Accept': '*/*', "Authorization": "OAuth %s" % self.token.token, 'Depth': 1}
        req = requests.Request("PROPFIND", self.url + path, headers=headers)
        with requests.Session() as s:
            resp = s.send(req.prepare())
            if resp.status_code == 207:
                print resp.content



if __name__ == "__main__":
    disk = YaDisk(LOGIN, PASSWORD)
    print disk.ls("/")