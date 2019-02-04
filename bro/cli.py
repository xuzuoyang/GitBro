import click
from tabulate import tabulate

from bro.core import (
    create_pull_request,
    get_pull_request,
)


@click.group()
def bro():
    pass


@bro.group()
def pr():
    """Pull Request Management CLI."""
    pass


@pr.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-u', '--user', required=True, type=str, help='Owner of the repo starting the pr.')
@click.option('-b', '--branch', required=True, type=str, help='Format as `local:remote`, default to `master:master`')
@click.option('--title', required=True, type=str, help='Title of the pr.')
@click.option('--body', type=str, help='Content body of the pr.')
@click.option('--mcm', type=bool, help='If maintainers can modify the pr, default to true.')
@click.option('--issue', type=int, help='Issue number to form the pr.')
def make(owner, repo, user, branch, title, body, mcm, issue):
    """Make a pull request.

    """
    branch_local, branch_remote = branch.split(':')
    head = '{user}:{branch}'.format(user=user, branch=branch_local)
    pull_request = create_pull_request(owner, repo, title, head=head,
                                       base=branch_remote, body, mcm, issue)
    click.echo(
        'Pull request {num} from {user}:{branch_local} to {owner}:{branch_remote} has been created!'.format(
            num=pull_request.number, user=user, branch_local=branch_local,
            owner=owner, branch_remote=branch_remote
        )
    )


@pr.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', help='Number of a pr.')
@click.option('-c', '--comments', help='Show comments of the pr.')
@click.option('-p', '--patch', is_flag=True, help='Show patch content of the pr.')
def show(owner, repo, num, comments, patch):
    """Show content of a pull request."""
    if patch:
        patch_content = get_pull_request(owner, repo, num, patch=True)
        click.echo_via_pager(patch_content)
    else:
        pull_request = get_pull_request(owner, repo, num)
        for key in ['meta', 'content']:
            attr = getattr(pull_request, key, {})
            click.echo(
                tabulate(list(attr.items()), tablefmt='grid'))


@pr.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, help='Number of a pr.')
@click.option('-c', '--comment', required=True, help='Content to comment.')
def comment(owner, repo, num, comment):
    """Comment on a pull request."""
    pass


@pr.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, help='Number of a pr.')
@click.option('--title', help='New title of the pr.')
@click.option('--body', help='New body of the pr.')
def modify(owner, repo, num):
    """Modify a pull request."""
    pass


@pr.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, help='Number of a pr.')
def close(owner, repo, num):
    """Close up a pull request."""
    pass


@pr.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, help='Number of a pr.')
def merge(owner, repo, num):
    """Merge a pull request."""
    pass


if __name__ == '__main__':
    pr = get_pull_request('harshasrinivas', 'cli-github', '7')
