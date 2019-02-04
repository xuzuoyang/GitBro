# gitbro

[![Build Status](https://travis-ci.org/xuzuoyang/bro.svg?branch=master)](https://travis-ci.org/xuzuoyang/mypackage)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

gitbro is an python package template for convenience of personal project development.

## Inspired by

- https://github.com/bast/somepackage
- https://docs.python-guide.org/writing/structure/
- https://www.makeareadme.com/
- https://keepachangelog.com/en/1.0.0/

## Installation

```bash
pip install bro
```

## Usage

```
>>> from bro import dict_substract
>>> dict_substract({}, {'a': 11})
{}
>>> dict_substract({'a': 12}, {'a': 11})
{'a': 12}
>>> dict_substract({'a': 11, 'b': 0}, {'a': 11})
{'b': 0}
```

## Support

python3.5+

## Roadmap

- [x] add tests.
- [x] add travis ci.
- [x] add use of tox.
- [ ] cookiecutter bro.

## Changelog

[Here](docs/CHANGELOG.md)

## License
[MIT](LICENSE)
