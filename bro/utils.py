from functools import partial, wraps
from sys import exit

from click import secho

from bro.exceptions import (BranchNotFound, GitCmdError, GitError,
                            RemoteNotFound)

print_normal = partial(secho, fg='green', bold=True)
print_error = partial(secho, fg='red', bold=True)


def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except GitError as e:
            error = e.message
            if isinstance(e, GitCmdError):
                error = f'{error}\nCommand: {" ".join(e.command)}'
            print_error(error)
            exit(1)

    return wrapper


def validate_branch(repo, *branches):
    try:
        for branch in branches:
            repo.get_branch(branch)
    except BranchNotFound:
        print_error(f'Branch {branch} does not exist.')
        exit(1)


def validate_remote(repo, *remotes):
    try:
        for remote in remotes:
            repo.get_repo(remote)
    except RemoteNotFound:
        print_error(f'Remote {remote} does not exist.')
        exit(1)
