#!/usr/bin/python
#coding: utf-8
import os
import random
import string
import unittest

from YaDiskClient import YaDisk, YaDiskException


LOGIN = os.environ.get('YANDEX_LOGIN')
PASSWORD = os.environ.get('YANDEX_PASSWORD')


class TestYaDisk(unittest.TestCase):
    remote_folder = '/TestYaDisk_{}'.format(''.join(random.choice(string.ascii_uppercase) for _ in range(6)))
    remote_file = 'TestYaDisk.py'
    remote_path = None
    tmp_remote_path = None
    tmp_local_file = None
    disk = None

    @classmethod
    def setUpClass(cls):
        cls.disk = YaDisk(LOGIN, PASSWORD)
        cls.remote_path = "{folder}/{file}".format(folder=cls.remote_folder, file=cls.remote_file)
        cls.tmp_remote_path = "{path}~".format(path=cls.remote_path)
        cls.tmp_local_file = "{file}~".format(file=cls.remote_file)

    def test_1df(self):
        result = self.disk.df()
        self.assertIsInstance(result, dict)
        self.assertTrue('available' in result.keys())
        self.assertTrue('used' in result.keys())

    def test_2mkdir(self):
        self.disk.mkdir(self.remote_folder)

        try:
            self.disk.mkdir('{folder}/dir/bad'.format(folder=self.remote_folder))
        except YaDiskException as e:
            self.assertEqual(e.code, 409)

        try:
            self.disk.mkdir(self.remote_folder)
        except YaDiskException as e:
            self.assertEqual(e.code, 405)

    def test_3upload(self):
        self.disk.upload(self.remote_file, self.remote_path)

    def test_4mv(self):
        self.disk.mv(self.remote_path , self.tmp_remote_path)

    def test_5cp(self):
        self.disk.cp(self.tmp_remote_path  , self.remote_path)

    def test_6ls(self):
        ls = self.disk.ls(self.remote_folder)
        self.assertEqual(len(ls), 3)
        self.assertEqual(ls[2]['length'], ls[1]['length'])

    def test_7download(self):
        self.disk.download(self.remote_path, self.tmp_local_file)

    def test_8rm(self):
        self.disk.rm(self.remote_folder)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.tmp_local_file)

if __name__ == '__main__':
    unittest.main()
