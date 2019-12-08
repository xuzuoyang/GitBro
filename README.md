# gitbro

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Gitbro is a cli management tool for better git workflow.

Typical workflows based on git might be:

1. Checkout to a new branch and work on it.
2. Commit all the dev code and push to your own repo.
3. `Start a pull request to the forked repo and let's say it gets merged.`
4. Delete the work branch and maybe its remote too.
5. Move to another task and repeat the cycle.

Or

1. Checkout to a new branch to work.
2. Commit and push to your own repo.
3. `Start a pull request to the master branch and gets merged.`
4. Delete this work branch.
5. All the same again from here.

## Installation

```bash
python setup.py install
```

## Usage

```bash
# Start dev branch based on upstream/master.
$ bro pickup dev --since master

# Sync from upstream/master, default to rebase. Add --merge to merge it.
$ bro pipeline --through master

# Delete both local and remote branch. Or keep rb with --keep-remote.
$ bro putout dev

# Make a pull request.
$ bro pull-request make OWNER --base master --open-browser

# Pull a pull request and apply to local repo.
$ bro pull-request get PR_ID feature-branch --checkout
```

## Support

python 3.7+

## Changelog

[Here](docs/CHANGELOG.md)

## License
[MIT](LICENSE)
