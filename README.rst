YaDiskClient
============

.. image:: https://travis-ci.org/TyVik/YaDiskClient.svg?branch=master
    :target: https://travis-ci.org/TyVik/YaDiskClient?branch=master
.. image:: https://coveralls.io/repos/github/TyVik/YaDiskClient/badge.svg?branch=master
    :target: https://coveralls.io/github/TyVik/YaDiskClient?branch=master
.. image:: https://img.shields.io/pypi/pyversions/YaDiskClient.svg
    :target: https://pypi.python.org/pypi/YaDiskClient/
.. image:: https://img.shields.io/pypi/v/YaDiskClient.svg
    :target: https://pypi.python.org/pypi/YaDiskClient/
.. image:: https://img.shields.io/pypi/status/YaDiskClient.svg
    :target: https://pypi.python.org/pypi/YaDiskClient/
.. image:: https://img.shields.io/pypi/l/YaDiskClient.svg
    :target: https://pypi.python.org/pypi/YaDiskClient/

Client for Yandex.Disk based on WebDav.

Install
=======

    pip install YaDiskClient

Source code
===========

    `github <https://github.com/TyVik/YaDiskClient>`_

    `explanatory article <https://tyvik.ru/posts/yandex-disk-python/>`_

Passwords and tokens
====================

You must use application password, not account password! Details - https://yandex.ru/support/id/authorization/app-passwords.html

Also, you can create OAuth-token for your application. Details - https://yandex.ru/dev/disk/doc/dg/concepts/quickstart.html

Both methods are supported. You should use method `set_login` or `set_token` before start.

Using API
=========

::

    from YaDiskClient.YaDiskClient import YaDisk
    disk = YaDisk()
    disk.set_auth(login, password)

    """
    Library also supports token authorization via:
    disk.set_token(token)
    """

    disk.df() # show used and available space

    disk.ls(path) # list of files/folder with attributes
    disk.mkdir(path) # create directory

    disk.rm(path) # remove file or directory
    disk.cp(src, dst) # copy from src to dst
    disk.mv(src, dst) # move from src to dst

    disk.upload(src, dst) # upload local file src to remote file dst
    disk.download(src, dst) # download remote file src to local file dst

    disk.publish_doc(path) # return public url
    disk.hide_doc(path) # remove public url form Yandex Disk

Tests
=====

For run tests:
    1. Set Yandex username and password in file tests/test_YaDiskClient.py
    2. python -m unittest discover -s tests -t tests
