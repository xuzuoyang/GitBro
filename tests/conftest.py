import os
import shutil
import pytest

from bro.git import GitRepo


@pytest.fixture
def git_repo(mocker):
    # TODO: context manager
    tmp_test_dir = '/tmp/gitbro_tests'
    git_db_dir = f'{tmp_test_dir}/.git'
    os.makedirs(tmp_test_dir, exist_ok=True)
    if os.path.exists(git_db_dir):
        shutil.rmtree(git_db_dir)
    shutil.copytree('./.git', git_db_dir)

    repo = GitRepo(tmp_test_dir)
    repo.executor = mocker.Mock()
    return repo
