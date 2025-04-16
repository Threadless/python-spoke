import os
from setuptools import setup, find_packages

setup(
    name             = 'Python-Spoke',
    version          = '1.0.29',
    packages         = find_packages(),
    description      = 'API bindings for Spoke API',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r').read(),
    license          = 'MIT',
    author           = 'Rob Hoelz',
    author_email     = 'rob.hoelz@skinnycorp.com',
    url              = 'https://github.com/Threadless/python-spoke',
    keywords         = 'spoke',
    install_requires = ['lxml==4.9.3', 'requests==2.27.0'],
    tests_require    = ['nose==1.3.7', 'rednose==1.3.0'],
)
