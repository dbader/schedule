import os
import sys
from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

SCHEDULE_VERSION = '0.2.1'
SCHEDULE_DOWNLOAD_URL = ('https://github.com/dbader/schedule/tarball/' +
                         SCHEDULE_VERSION)

setup(
    name='schedule',
    packages=['schedule'],
    version=SCHEDULE_VERSION,
    description='Job scheduling for humans.',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('HISTORY.rst').read()),
    license=open('LICENSE.txt').read(),
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
        'Programming Language :: Python :: 3.3',
        'Natural Language :: English',
    ],
)
