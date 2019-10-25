from logging import getLogger
from os.path import abspath

from git import RemoteProgress, Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from git.repo.fun import BadName

from bro.exceptions import (BranchAlreadyExists, BranchCreateError,
                            BranchNotFound, GitCmdError, InvalidGitRepo,
                            RemoteNotFound)

LOGGER = getLogger(__name__)


class ProgressDisplayer(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        progress = max(int((100 * cur_count) // max_count), 1)
        end = '' if progress != 100 else '\n'
        LOGGER.info('#' * progress, '\r', end=end)


class GitRepo:
    def __init__(self, repo_path):
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            abs_path = abspath(repo_path)
            raise InvalidGitRepo(f'Path {abs_path} is not a git repo.')
        self.executor = self.repo.git

    @classmethod
    def from_path(cls, path):
        return cls(path)

    @property
    def current_branch(self):
        return self.repo.active_branch

    def get_branch(self, branch):
        try:
            return self.repo.heads[branch]
        except IndexError:
            raise BranchNotFound(f'Cannot find branch {branch}.')

    def get_remote(self, remote):
        try:
            return self.repo.remotes[remote]
        except IndexError:
            raise RemoteNotFound(f'Remote {remote} does not exist.')

    def fetch(self, remote, branch='*'):
        try:
            remote_ref = self.get_remote(remote)
            refspec = f'refs/heads/{branch}:refs/remotes/{remote}/{branch}'
            for info in remote_ref.fetch(refspec,
                                         progress=ProgressDisplayer()):
                LOGGER.info(f'Fetched {info.name} to {info.commit}.')
        except GitCommandError as e:
            raise GitCmdError(f'Failed to fetch {remote}/{branch}.',
                              command=e.command)

    def push(self, remote, branch, delete=False):
        args = [remote, branch]
        if delete:
            args.append('--delete')

        try:
            self.executor.push(args)
        except GitCommandError as e:
            if delete:
                error_msg = f'Failed to delete {remote}/{branch}.'
            else:
                error_msg = f'Failed to push to {remote}/{branch}.'
            raise GitCmdError(error_msg, command=e.command)

        if delete:
            LOGGER.info(f'Deleted {remote}/{branch}.')
        else:
            LOGGER.info(f'Pushed to {remote}/{branch}.')

    def pull(self, remote, branch, rebase=False):
        args = [remote, branch]
        if rebase:
            args.append('--rebase')

        try:
            self.executor.pull(args)
        except GitCommandError as e:
            if rebase:
                error_msg = f'Failed to pull(rebase) {remote}/{branch}.'
            else:
                error_msg = f'Failed to pull {remote}/{branch}.'
            raise GitCmdError(error_msg, command=e.command)

        if rebase:
            LOGGER.info(f'Rebased upon {remote}/{branch}.')
        else:
            LOGGER.info(f'Pulled from {remote}/{branch}.')

    def branch_create(self, branch, start_point=None):
        # TODO: set tracking branch
        try:
            assert branch not in self.repo.heads
            if start_point:
                branch_ref = self.repo.create_head(branch, commit=start_point)
                LOGGER.info(f'Created branch {branch} based on {start_point}.')
            else:
                branch_ref = self.repo.create_head(branch)
                LOGGER.info(f'Created branch {branch}.')
        except AssertionError:
            raise BranchAlreadyExists(f'Branch {branch} already exists.')
        except BadName:
            raise BranchCreateError(
                f'Unable to create branch from {start_point}.')

        return branch_ref

    def branch_checkout(self, branch, create=False, start_point=None):
        try:
            if create:
                self.branch_create(branch, start_point)

            checked_out = self.get_branch(branch).checkout()
            LOGGER.info(f'Switched to branch {branch}.')
        except GitCommandError as e:
            raise GitCmdError(f'Failed to checkout to branch {branch}.',
                              command=e.command)

        return checked_out

    def branch_delete(self, branch, force=False):
        try:
            self.get_branch(branch)
            self.repo.delete_head(branch, force=force)
        except GitCommandError as e:
            raise GitCmdError(f'Failed to delete branch {branch}.',
                              command=e.command)

        LOGGER.info(f'Deleted local branch {branch}.')

    def merge(self, branch):
        try:
            master, subster = self.current_branch, self.get_branch(branch)
            merge_base = self.repo.merge_base(master, subster)
            self.repo.index.merge_tree(subster, base=merge_base)
            return self.repo.index.commit(
                f'Merged {master.name} with {branch} by gitbro.',
                parent_commits=(master.commit, subster.commit))
        except GitCommandError as e:
            raise GitCmdError(f'Failed to merge {subster} into {master}.',
                              command=e.command)
