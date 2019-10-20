from setuptools import find_packages, setup

NAME = 'gitbro'
VERSION = '0.0.1'
DESCRIPTION = 'Git management tool for better workflow.'
AUTHOR = 'xzy'
EMAIL = 'xuzuoyang@gmail.com'
URL = 'https://github.com/xuzuoyang/gitbro'

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      python_requires='>=3.7.0',
      url=URL,
      packages=find_packages(exclude=('tests', )),
      entry_points={
          'console_scripts': ['bro=bro.cli:bro'],
      },
      install_requires=['requests', 'click', 'tabulate'],
      extras_require={'test': ['pytest', 'pytest-cov', 'pytest-mock']},
      include_package_data=True,
      license='MIT')
