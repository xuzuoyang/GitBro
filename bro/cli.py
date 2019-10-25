'''This module contains cli functions.'''

import click
from click import argument, command, option
from tabulate import tabulate

from bro.git import GitRepo
from bro.hub import (comment_pull_request, create_pull_request,
                     get_pull_request, merge_pull_request, update_pull_request)
from bro.utils import error_handler, print_normal, validate_branch

REMOTE_UPSTREAM = 'upstream'
REMOTE_ORIGIN = 'origin'
BRANCH_MAIN = 'master'


class AliasedGroup(click.Group):

    ALIAS = {
        'pu': 'pickup',
        'pl': 'pipeline',
        'po': 'putout',
        'pr': 'pull-request'
    }

    def get_command(self, ctx, cmd_name):
        cmd_name = self.ALIAS.get(cmd_name) or cmd_name
        return super().get_command(ctx, cmd_name)


@command(cls=AliasedGroup)
@option('-p', '--path', default='.')
@click.pass_context
@error_handler
def bro(ctx, path):
    '''Git workflow management tool.'''
    ctx.obj = GitRepo.from_path(path)


@bro.command()
@argument('branch')
@option('-s',
        '--since',
        type=str,
        default='master',
        help='Start point of the new branch, default master.')
@click.pass_obj
@error_handler
def pickup(repo, branch, since):
    '''Start a new branch to work on.'''
    validate_branch(repo, since)

    repo.fetch(REMOTE_UPSTREAM, since)
    remote_branch = f'{REMOTE_UPSTREAM}/{since}'
    print_normal(f'Fetched remote branch {remote_branch}.')

    repo.branch_checkout(branch, create=True, start_point=remote_branch)
    print_normal(f'Start branch {branch} from {remote_branch}.')
    print_normal(f'You are in branch {branch} now.')


@bro.command()
@option('-t',
        '--through',
        default='master',
        help='Remote branch to sync from.')
@option('-m', '--merge', is_flag=True, help='Merge instead of rebase.')
@click.pass_obj
@error_handler
def pipeline(repo, through, merge):
    '''Sync with certain remote branch.'''
    validate_branch(repo, through)

    repo.pull(REMOTE_UPSTREAM, through, rebase=not merge)
    method = 'merged' if merge else 'rebased'
    print_normal(f'Synced from {REMOTE_UPSTREAM}/{through} ({method}).')


@bro.command()
@argument('branch')
@option('-k', '--keep-remote', is_flag=True, help='Keep remote branch.')
@click.pass_obj
@error_handler
def putout(repo, branch, keep_remote):
    '''End the branch after finishing the task.'''
    validate_branch(repo, branch)

    repo.branch_checkout(BRANCH_MAIN)
    print_normal(f'Checked out to branch {BRANCH_MAIN}.')

    repo.pull(REMOTE_UPSTREAM, BRANCH_MAIN)
    print_normal(f'Synced from remote {REMOTE_UPSTREAM} (rebased).')

    repo.branch_delete(branch)
    print_normal(f'Deleted local branch {branch}.')
    if not keep_remote:
        repo.push(REMOTE_ORIGIN, branch, delete=True)
        print_normal(f'Deleted remote branch {REMOTE_ORIGIN}/{branch}.')


@bro.group()
@argument('owner')
@argument('repo')
@click.pass_context
def pull_request(ctx, owner, repo):
    '''Manage pull requests of github.'''
    ctx.obj = {'owner': owner, 'repo': repo}


@pull_request.command()
@option('-u',
        '--user',
        required=True,
        type=str,
        help='Owner of the repo starting the pr.')
@option('-p', '--password', prompt=True, hide_input=True)
@option('-b',
        '--branch',
        required=True,
        type=str,
        help='Format as `local:remote`, default to `master:master`')
@option('--title', required=True, type=str, help='Title of the pr.')
@option('--body', type=str, help='Content body of the pr.')
@option('--mcm',
        type=bool,
        default=False,
        help='If maintainers can modify the pr, default to true.')
@option('--issue', type=int, help='Issue number to form the pr.')
@click.pass_obj
def make(state, user, branch, title, body, mcm, issue, password):
    '''Make a pull request.

    '''
    owner, repo = state['owner'], state['repo']
    branch_local, branch_remote = branch.split(':')
    head = '{user}:{branch}'.format(user=user, branch=branch_local)
    pull_request = create_pull_request(owner,
                                       repo,
                                       title,
                                       head=head,
                                       base=branch_remote,
                                       auth=(user, password),
                                       body=body,
                                       mcm=mcm,
                                       issue=issue)
    click.echo(
        'Pull request {num} from {user}:{branch_local} to {owner}:{branch_remote} has been created!'  # noqa
        .format(owner=owner,
                user=user,
                num=pull_request.number,
                branch_local=branch_local,
                branch_remote=branch_remote))


@pull_request.command()
@argument('owner')
@argument('repo')
@option('-n', '--num', help='Number of a pr.')
@option('-p', '--patch', is_flag=True, help='Show patch content of the pr.')
@click.pass_obj
def show(state, num, patch):
    '''Show content of a pull request.'''
    owner, repo = state['owner'], state['repo']
    if patch:
        patch_content = get_pull_request(owner, repo, num, patch=True)
        click.echo_via_pager(patch_content)
    else:
        pull_request = get_pull_request(owner, repo, num)
        for key in ['meta', 'content']:
            attr = getattr(pull_request, key, {})
            click.echo(tabulate(list(attr.items()), tablefmt='grid'))


@pull_request.command()
@option('-n', '--num', required=True, help='Number of a pr.')
@option('-u',
        '--user',
        required=True,
        type=str,
        help='Owner of the repo starting the pr.')
@option('-p', '--password', prompt=True, hide_input=True)
@option('-c', '--content', required=True, help='Content to comment.')
@click.pass_obj
def comment(state, num, user, password, content):
    '''Comment on a pull request.'''
    owner, repo = state['owner'], state['repo']
    response = comment_pull_request(owner,
                                    repo,
                                    num,
                                    auth=(user, password),
                                    comment=content)
    data = [
        ('comment', content),
        ('url', response['html_url']),
        ('created_at', response['created_at']),
        ('updated_at', response['updated_at']),
    ]
    click.echo(tabulate(data, tablefmt='grid'))


@pull_request.command()
@option('-n', '--num', required=True, help='Number of a pr.')
@option('-u',
        '--user',
        required=True,
        type=str,
        help='Owner of the repo starting the pr.')
@option('-p', '--password', prompt=True, hide_input=True)
@option('--title', help='New title of the pr.')
@option('--body', help='New body of the pr.')
@option('--mcm/--no-mcm',
        default=True,
        help='If maintainers can modify the pr.')
@click.pass_obj
def update(state, num, user, password, title, body, mcm):
    '''Modify a pull request.'''
    owner, repo = state['owner'], state['repo']
    pull_request = update_pull_request(owner,
                                       repo,
                                       num,
                                       auth=(user, password),
                                       title=title,
                                       body=body,
                                       maintainer_can_modify=mcm)
    content = getattr(pull_request, 'content', {})
    click.echo(tabulate(list(content.items()), tablefmt='grid'))


@pull_request.command()
@option('-n', '--num', required=True, type=str, help='Number of a pr.')
@option('-u',
        '--user',
        required=True,
        type=str,
        help='Owner of the repo starting the pr.')
@option('-p', '--password', prompt=True, hide_input=True)
@option('--close', 'state', flag_value='closed', default=True)
@option('--open', 'state', flag_value='open')
@click.pass_obj
def toggle(state_obj, num, user, password, state):
    '''Close a pull request.'''
    owner, repo = state_obj['owner'], state_obj['repo']
    pull_request = update_pull_request(owner,
                                       repo,
                                       num,
                                       auth=(user, password),
                                       state=state)
    content = getattr(pull_request, 'meta', {})
    click.echo(tabulate(list(content.items()), tablefmt='grid'))


@pull_request.command()
@option('-n', '--num', required=True, help='Number of a pr.')
@option('-u',
        '--user',
        required=True,
        type=str,
        help='Owner of the repo starting the pr.')
@option('-p', '--password', prompt=True, hide_input=True)
@option('-m', '--message', type=str, help='Merge commit message.')
@click.pass_obj
def merge(state, num, user, password, message):
    '''Merge a pull request.'''
    owner, repo = state['owner'], state['repo']
    response = merge_pull_request(owner,
                                  repo,
                                  num,
                                  auth=(user, password),
                                  commit_message=message)
    click.echo(response['message'])
