import os

from setuptools import find_packages, setup

NAME = 'gitbro'
DESCRIPTION = 'Lightweight cli tool for pull request management.'
URL = 'https://github.com/xuzuoyang/gitbro'
EMAIL = 'xuzuoyang@gmail.com'
AUTHOR = 'xzy'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None

REQUIRED = ['requests', 'click', 'tabulate']

here = os.path.abspath(os.path.dirname(__file__))

about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    entry_points={
        'console_scripts': ['bro=bro.cli:bro'],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT'
)
