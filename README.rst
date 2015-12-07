YaDiskClient
============

Client for Yandex.Disk based on WebDav.

Install
=======

    `pip <https://pypi.python.org/pypi/pip/>`_ install
    `YaDiskClient <https://pypi.python.org/pypi/YaDiskClient>`_

or

    `easy\_install <https://pypi.python.org/pypi/setuptools>`_
    `YaDiskClient <https://pypi.python.org/pypi/YaDiskClient>`_

or

    python setup.py install

Source code

    `github <https://github.com/TyVik/YaDiskClient>`_

Using API
=========

::

    from YaDiskClient.YaDiskClient import YaDisk
    disk = YaDisk(login, password)

    disk.df() # show used and available space
    disk.ls(path) # list of files/folder with attributes
    disk.mkdir(path) # create directory
    disk.rm(path) # delete file or directory
    disk.cp(src, dst) # copy from src to dst
    disk.mv(src, dst) # move from src to dst
    disk.upload(src, dst) # upload local file src to remote file dst
    disk.download(src, dst) # download remote file src to local file dst

Tests
=====

For run tests set Yandex username and password in file TestYaDisk.py.
