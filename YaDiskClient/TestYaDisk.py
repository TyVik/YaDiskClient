#!/usr/bin/python
#coding: utf-8
import os
import unittest
from YaDiskClient import YaDisk, YaDiskException


LOGIN = None
PASSWORD = None


class TestYaDisk(unittest.TestCase):
    testFolder = '/TestYaDisk'
    testFile = 'TestYaDisk.py'
    disk = None

    @classmethod
    def setUpClass(cls):
        cls.disk = YaDisk(LOGIN, PASSWORD)

    def test_1df(self):
        result = self.disk.df()
        self.assertIsInstance(result, dict)
        self.assertTrue('available' in result.keys())
        self.assertTrue('used' in result.keys())

    def test_2mkdir(self):
        self.disk.mkdir(self.testFolder)

        try:
            self.disk.mkdir('%s/dir/bad' % self.testFolder)
        except YaDiskException as e:
            self.assertEqual(e.code, 409)

        try:
            self.disk.mkdir(self.testFolder)
        except YaDiskException as e:
            self.assertEqual(e.code, 405)

    def test_3upload(self):
        self.disk.upload(self.testFile, "%s/%s" % (self.testFolder, self.testFile))

    def test_4mv(self):
        self.disk.mv("%s/%s" % (self.testFolder, self.testFile), "%s/%s~" % (self.testFolder, self.testFile))

    def test_5cp(self):
        self.disk.cp("%s/%s~" % (self.testFolder, self.testFile), "%s/%s" % (self.testFolder, self.testFile))

    def test_6ls(self):
        ls = self.disk.ls(self.testFolder)
        self.assertEqual(len(ls), 3)
        self.assertEqual(ls[2]['length'], ls[1]['length'])

    def test_7download(self):
        self.disk.download("%s/%s" % (self.testFolder, self.testFile), "%s~" % self.testFile)

    def test_8rm(self):
        self.disk.rm(self.testFolder)

    @classmethod
    def tearDownClass(cls):
        os.remove("%s~" % cls.testFile)

if __name__ == '__main__':
    unittest.main()