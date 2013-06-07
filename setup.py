import os
import sys
from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r PyPI')
    sys.exit()

setup(
    name='schedule',
    packages=['schedule'],
    version='0.1.10',
    description='Job scheduling for humans.',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('HISTORY.rst').read()),
    license=open('LICENSE.txt').read(),
    author='Daniel Bader',
    author_email='mail@dbader.org',
    url='https://github.com/dbader/schedule',
    download_url='https://github.com/dbader/schedule/tarball/0.1.9',
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
