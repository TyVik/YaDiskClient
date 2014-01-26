#-*- coding: utf-8 -*-
from setuptools import setup, find_packages
import YaDiskClient

setup(
    name='YaDiskClient',
    version=YaDiskClient.__version__,
    include_package_data=True,
    py_modules=['YaDiskClient'],
    url='https://github.com/TyVik/YaDiskClient',
    license='MIT',
    author='TyVik',
    author_email='tyvik8@gmail.com',
    description='Clent for Yandex.Disk',
    long_description=open('README.rst').read(),
    install_requires=['requests', 'lxml'],
    packages=find_packages(),
#    test_suite='YaDiskClient.TestYaDisk' # this line is commented because tests needs Yandex login and password
)
