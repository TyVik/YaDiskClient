#!/usr/bin/env python
# coding: utf-8

import os
import random
import string
import unittest

from YaDiskClient.YaDiskClient import YaDisk, YaDiskException


LOGIN = os.environ.get('YANDEX_LOGIN')
PASSWORD = os.environ.get('YANDEX_PASSWORD')


class TestYaDisk(unittest.TestCase):
    disk = None
    remote_folder = None
    remote_file = None
    remote_path = None

    @classmethod
    def setUpClass(cls):
        cls.disk = YaDisk(LOGIN, PASSWORD)
        # take any file in work directory
        for item in os.listdir('.'):
            if os.path.isfile(item):
                cls.remote_file = item
                break

        cls.remote_folder = '/TestYaDisk_{}'.format(''.join(random.choice(string.ascii_uppercase) for _ in range(6)))
        cls.remote_path = "{folder}/{file}".format(folder=cls.remote_folder, file=cls.remote_file)

    def test_00main(self):
        def mkdir(remote_folder):
            self.disk.mkdir(remote_folder)

            try:
                self.disk.mkdir('{folder}/dir/bad'.format(folder=remote_folder))
            except YaDiskException as e:
                self.assertEqual(e.code, 409)

            try:
                self.disk.mkdir(remote_folder)
            except YaDiskException as e:
                self.assertEqual(e.code, 405)

        tmp_remote_path = "{path}~".format(path=self.remote_path)
        tmp_local_file = "{file}~".format(file=self.remote_file)
        
        mkdir(self.remote_folder)
        self.disk.upload(self.remote_file, self.remote_path)
        self.disk.mv(self.remote_path, tmp_remote_path)
        self.disk.cp(tmp_remote_path, self.remote_path)

        ls = self.disk.ls(self.remote_folder)
        self.assertEqual(len(ls), 3)
        self.assertEqual(ls[2]['length'], ls[1]['length'])

        self.disk.download(self.remote_path, tmp_local_file)
        self.disk.rm(self.remote_folder)
        os.remove(tmp_local_file)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.tmp_local_file)


if __name__ == '__main__':
    unittest.main()
