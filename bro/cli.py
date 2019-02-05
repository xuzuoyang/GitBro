'''This module contains cli functions.'''

import click
from tabulate import tabulate

from bro.core import (
    create_pull_request,
    get_pull_request,
    update_pull_request,
    comment_pull_request,
    merge_pull_request,
)


@click.group()
def bro():
    """Pull Request Management CLI."""
    pass


@bro.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-u', '--user', required=True, type=str, help='Owner of the repo starting the pr.')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-b', '--branch', required=True, type=str, help='Format as `local:remote`, default to `master:master`')
@click.option('--title', required=True, type=str, help='Title of the pr.')
@click.option('--body', type=str, help='Content body of the pr.')
@click.option('--mcm', type=bool, default=False, help='If maintainers can modify the pr, default to true.')
@click.option('--issue', type=int, help='Issue number to form the pr.')
def make(owner, repo, user, branch, title, body, mcm, issue, password):
    """Make a pull request.

    """
    branch_local, branch_remote = branch.split(':')
    head = '{user}:{branch}'.format(user=user, branch=branch_local)
    pull_request = create_pull_request(
        owner, repo, title, head=head, base=branch_remote,
        auth=(user, password), body=body, mcm=mcm, issue=issue
    )
    click.echo(
        'Pull request {num} from {user}:{branch_local} to {owner}:{branch_remote} has been created!'.format(
            owner=owner, user=user, num=pull_request.number,
            branch_local=branch_local, branch_remote=branch_remote
        )
    )


@bro.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', help='Number of a pr.')
@click.option('-p', '--patch', is_flag=True, help='Show patch content of the pr.')
def show(owner, repo, num, patch):
    """Show content of a pull request."""
    if patch:
        patch_content = get_pull_request(owner, repo, num, patch=True)
        click.echo_via_pager(patch_content)
    else:
        pull_request = get_pull_request(owner, repo, num)
        for key in ['meta', 'content']:
            attr = getattr(pull_request, key, {})
            click.echo(tabulate(list(attr.items()), tablefmt='grid'))


@bro.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, help='Number of a pr.')
@click.option('-u', '--user', required=True, type=str, help='Owner of the repo starting the pr.')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-c', '--content', required=True, help='Content to comment.')
def comment(owner, repo, num, user, password, content):
    """Comment on a pull request."""
    response = comment_pull_request(
        owner, repo, num,
        auth=(user, password),
        comment=content
    )
    data = [
        ('comment', content),
        ('url', response['html_url']),
        ('created_at', response['created_at']),
        ('updated_at', response['updated_at']),
    ]
    click.echo(tabulate(data, tablefmt='grid'))

@bro.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, help='Number of a pr.')
@click.option('-u', '--user', required=True, type=str, help='Owner of the repo starting the pr.')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('--title', help='New title of the pr.')
@click.option('--body', help='New body of the pr.')
@click.option('--mcm/--no-mcm', default=True, help='If maintainers can modify the pr.')
def update(owner, repo, num, user, password, title, body, mcm):
    """Modify a pull request."""
    pull_request = update_pull_request(
        owner, repo, num,
        auth=(user, password),
        title=title, body=body, maintainer_can_modify=mcm
    )
    content = getattr(pull_request, 'content', {})
    click.echo(tabulate(list(content.items()), tablefmt='grid'))


@bro.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, type=str, help='Number of a pr.')
@click.option('-u', '--user', required=True, type=str, help='Owner of the repo starting the pr.')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('--close', 'state', flag_value='closed', default=True)
@click.option('--open', 'state', flag_value='open')
def toggle(owner, repo, num, user, password, state):
    """Close a pull request."""
    pull_request = update_pull_request(
        owner, repo, num,
        auth=(user, password),
        state=state
    )
    content = getattr(pull_request, 'meta', {})
    click.echo(tabulate(list(content.items()), tablefmt='grid'))


@bro.command()
@click.argument('owner')
@click.argument('repo')
@click.option('-n', '--num', required=True, help='Number of a pr.')
@click.option('-u', '--user', required=True, type=str, help='Owner of the repo starting the pr.')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-m', '--message', type=str, help='Merge commit message.')
def merge(owner, repo, num, user, password, message):
    """Merge a pull request."""
    response = merge_pull_request(
        owner, repo, num,
        auth=(user, password),
        commit_message=message
    )
    click.echo(response['message'])
