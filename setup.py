import os
from setuptools import setup, find_packages

setup(
    name             = 'Spoke',
    version          = '0.1',
    packages         = find_packages(),
    description      = 'API bindings for Spoke API',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r').read(),
    license          = 'MIT',
    author           = 'Rob Hoelz',
    author_email     = 'rob.hoelz@skinnycorp.com',
    url              = 'https://github.com/Threadless/python-spoke',
    keywords         = 'spoke',
    install_requires = ['lxml==3.3.5', 'requests==2.2.1'],
    tests_require    = ['unittest2==0.5.1', 'nose==1.3.1', 'python-termstyle==0.1.10', 'rednose==0.4.1'],
)
