import os
from setuptools import setup, find_packages

setup(
    name             = 'Python-Spoke',
    version          = '1.0.22',
    packages         = find_packages(),
    description      = 'API bindings for Spoke API',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r').read(),
    license          = 'MIT',
    author           = 'Rob Hoelz',
    author_email     = 'rob.hoelz@skinnycorp.com',
    url              = 'https://github.com/Threadless/python-spoke',
    keywords         = 'spoke',
    install_requires = ['lxml==4.6.3', 'requests==2.20.0'],
    tests_require    = ['nose==1.3.1', 'python-termstyle==0.1.10', 'rednose==0.4.1'],
)
