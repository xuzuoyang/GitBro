class GitError(Exception):
    def __init__(self, message):
        self.message = message


class InvalidGitRepo(GitError):
    pass


class BranchNotFound(GitError):
    pass


class BranchAlreadyExists(GitError):
    pass


class BranchCreateError(GitError):
    pass


class RemoteNotFound(GitError):
    pass


class GitCmdError(GitError):
    def __init__(self, message, command):
        super().__init__(message)
        self.command = command


class GithubError(Exception):
    pass
