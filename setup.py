import codecs
import os
import sys
from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

SCHEDULE_VERSION = '0.3.1'
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
    long_description=(
        read_file('README.rst') + '\n\n' +
        read_file('HISTORY.rst')
    ),
    license=read_file('LICENSE.txt'),
    author='Daniel Bader',
    author_email='mail@dbader.org',
    url='https://github.com/dbader/schedule',
    download_url=SCHEDULE_DOWNLOAD_URL,
    keywords=[
        'schedule', 'periodic', 'jobs', 'scheduling', 'clockwork',
        'cron'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Natural Language :: English',
    ],
)
