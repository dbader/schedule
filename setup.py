"""
Publish a new version:

$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags

$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel --universal
$ twine upload dist/*
"""
import codecs
import os
import sys
from setuptools import setup


SCHEDULE_VERSION = '0.4.3'
SCHEDULE_DOWNLOAD_URL = (
    'https://github.com/dbader/schedule/tarball/' + SCHEDULE_VERSION
)

def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()

setup(
    name='schedule',
    packages=['schedule'],
    version=SCHEDULE_VERSION,
    description='Job scheduling for humans.',
    long_description=read_file('README.rst'),
    license='MIT',
    author='Daniel Bader',
    author_email='mail@dbader.org',
    url='https://github.com/dbader/schedule',
    download_url=SCHEDULE_DOWNLOAD_URL,
    keywords=[
        'schedule', 'periodic', 'jobs', 'scheduling', 'clockwork',
        'cron', 'scheduler', 'job scheduling'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
    ],
)
