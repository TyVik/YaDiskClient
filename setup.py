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
    install_requires=['requests'],
    packages=find_packages(),
    keywords='Yandex.Disk, webdav, client, python, Yandex'
#    test_suite='YaDiskClient.TestYaDisk' # this line is commented because tests needs Yandex login and password
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: System :: Archiving :: Backup',
    ],
)
