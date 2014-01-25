#!/usr/bin/python
#coding: utf-8
import requests
import time
from YaDiskSettings import APP_ID, APP_SECRET, LOGIN, PASSWORD


class YaDiskException(Exception):
    pass


class YaDisk(object):
    login = None
    password = None
    # app_id = APP_ID
    # app_secret = APP_SECRET
    url = "https://webdav.yandex.ru"
    
    def __init__(self, login, password):
        super(YaDisk, self).__init__()
        self.login = login
        self.password = password

    def ls(self, path):
        headers = {'Accept': '*/*', 'Depth': 1}
        req = requests.Request("PROPFIND", self.url + path, headers=headers, auth=(self.login, self.password))
        with requests.Session() as s:
            resp = s.send(req.prepare())
            if resp.status_code == 207:
                print resp.content



if __name__ == "__main__":
    disk = YaDisk(LOGIN, PASSWORD)
    print disk.ls("/")