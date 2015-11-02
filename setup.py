#-*- coding: utf-8 -*-
from setuptools import setup, find_packages
import codecs
import os
import re


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")
    
setup(
    name='YaDiskClient',
    version=find_version('YaDiskClient', '__init__.py'),
    include_package_data=True,
    py_modules=['YaDiskClient'],
    url='https://github.com/TyVik/YaDiskClient',
    license='MIT',
    author='TyVik',
    author_email='tyvik8@gmail.com',
    description='Clent for Yandex.Disk',
    long_description=open('README.rst').read(),
    install_requires=['requests'],
    packages=find_packages(),
#    test_suite='YaDiskClient.TestYaDisk' # this line is commented because tests needs Yandex login and password
)
