from git import RemoteProgress, Repo


class ProgressDisplayer(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        progress = max(int((100 * cur_count) // max_count), 1)
        end = '' if progress != 100 else '\n'
        print('#' * progress, '\r', end=end)


class GitRepo:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)
        self.executor = self.repo.git

    @classmethod
    def from_path(cls, path):
        return cls(path)

    def fetch(self, remote, branch='*'):
        refspec = f'refs/heads/{branch}:refs/remotes/{remote}/{branch}'
        remote_ref = self.repo.remotes[remote]
        for info in remote_ref.fetch(refspec, progress=ProgressDisplayer()):
            print(f'Fetched {info.name} to {info.commit}.')

    def push(self, remote, branch, delete=False):
        args = [remote, branch]
        if delete:
            args.append('--delete')

        self.executor.push(args)
        if delete:
            print(f'Deleted {remote}/{branch}.')
        else:
            print(f'Pushed to {remote}/{branch}.')

    def pull(self, remote, branch, rebase=False):
        args = [remote, branch]
        if rebase:
            args.append('--rebase')

        self.executor.pull(args)
        if rebase:
            print(f'Rebased upon {remote}/{branch}.')
        else:
            print(f'Pulled from {remote}/{branch}.')

    def branch_create(self, branch, start_point=None):
        # TODO: set tracking branch
        if start_point:
            branch_ref = self.repo.create_head(branch, commit=start_point)
            print(f'Created branch {branch} based on {start_point}.')
        else:
            branch_ref = self.repo.create_head(branch)
            print(f'Created branch {branch}.')

        return branch_ref

    def branch_checkout(self, branch, create=False, start_point=None):
        if create:
            branch_ref = self.branch_create(branch, start_point)
        else:
            branch_ref = self.repo.heads[branch]

        print(f'Switched to branch {branch}.')
        return branch_ref.checkout()

    def branch_delete(self,
                      branch,
                      remote=None,
                      force=False,
                      include_remote=False):
        self.repo.delete_head(branch, force=force)
        if remote and include_remote:
            self.push(remote, branch, delete=True)

        print(f'Deleted local branch {branch}.')
