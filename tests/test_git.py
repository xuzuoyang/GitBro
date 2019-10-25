import logging

import git
import pytest


@pytest.mark.usefixtures('git_repo')
class TestGitBranch:

    TEST_BRANCH = 'test'

    # TODO: context manager
    def clean_branch(self, git_repo, branch):
        if branch in [h.name for h in git_repo.repo.heads]:
            git_repo.branch_delete(branch, force=True)

    def test_create(self, git_repo):
        self.clean_branch(git_repo, self.TEST_BRANCH)

        branch_ref = git_repo.branch_create(self.TEST_BRANCH)
        assert isinstance(branch_ref, git.refs.head.Head)
        assert branch_ref.name == self.TEST_BRANCH

        assert git_repo.repo.head.ref != branch_ref
        branch_ref = git_repo.branch_checkout(self.TEST_BRANCH)
        assert git_repo.repo.head.ref == branch_ref

        git_repo.branch_checkout('master')
        git_repo.branch_delete(self.TEST_BRANCH, force=True)
        assert branch_ref not in git_repo.repo.heads

    def test_create_on_commit(self, git_repo):
        pass

    def test_create_before_checkout(self, git_repo):
        self.clean_branch(git_repo, self.TEST_BRANCH)
        branch_ref = git_repo.branch_checkout(self.TEST_BRANCH, create=True)
        assert git_repo.repo.head.ref == branch_ref


@pytest.mark.usefixtures('git_repo')
class TestGitRemote:
    def test_fetch(self, git_repo, caplog):
        with caplog.at_level(logging.INFO):
            git_repo.fetch('origin', 'master')

        assert 'Fetched origin/master' in caplog.text

    @pytest.mark.parametrize(
        'args, push_args, output',
        [(['origin', 'master'], ['origin', 'master'
                                 ], 'Pushed to origin/master.'),
         (['origin', 'master', True], ['origin', 'master', '--delete'
                                       ], 'Deleted origin/master.')])
    def test_push(self, git_repo, args, push_args, output, caplog):
        with caplog.at_level(logging.INFO):
            git_repo.push(*push_args)
            git_repo.executor.push.assert_called_once_with(push_args)

        assert output in caplog.text

    @pytest.mark.parametrize(
        'args, pull_args, output',
        [(['origin', 'master'], ['origin', 'master'
                                 ], 'Pulled from origin/master.'),
         (['origin', 'master', True], ['origin', 'master', '--rebase'
                                       ], 'Rebased upon origin/master.')])
    def test_pull(self, git_repo, args, pull_args, output, caplog):
        with caplog.at_level(logging.INFO):
            git_repo.pull(*pull_args)
            git_repo.executor.pull.assert_called_once_with(pull_args)

        assert output in caplog.text
