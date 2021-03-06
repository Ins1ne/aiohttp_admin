import os
import re
import sys
from setuptools import setup, find_packages


PY_VER = sys.version_info

if not PY_VER >= (3, 5):
    raise RuntimeError("aiohttp_admin doesn't support Python earlier than 3.5")


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


install_requires = ['aiohttp',
                    'trafaret',
                    'python-dateutil',
                    'aiohttp_jinja2']

extras_require = {'motor': ['motor'],
                  'aiopg': ['aiopg', 'sqlalchemy'],
                  'aiomysql': ['aiomysql', 'sqlalchemy']}


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__),
                           'aiohttp_admin', '__init__.py')
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        else:
            msg = 'Cannot find version in aiohttp_admin/__init__.py'
            raise RuntimeError(msg)


classifiers = [
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Operating System :: POSIX',
    'Environment :: Web Environment',
    'Development Status :: 3 - Alpha',
    'Topic :: Database',
    'Topic :: Database :: Front-Ends',
]


setup(name='aiohttp_admin',
      version=read_version(),
      description=('admin interface for aiohttp application'),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=classifiers,
      platforms=['POSIX'],
      author="Nikolay Novik",
      author_email="nickolainovik@gmail.com",
      url='https://github.com/jettify/aiohttp_admin',
      download_url='',
      license='Apache 2',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require=extras_require,
      include_package_data=True)
