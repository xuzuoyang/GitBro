'''This module contains cli functions.'''

from pathlib import Path
from configparser import ConfigParser
from webbrowser import open_new
import click
from click import argument, command, option
from tabulate import tabulate

from bro.git import GitRepo
from bro.hub import (request_github_access_token, create_pull_request)
from bro.utils import error_handler, print_normal, print_error, validate_branch, get_pr_msg

CONFIG_FILE = Path.home() / '.config/bro'

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
    config_parser = ConfigParser()
    if not CONFIG_FILE.exists():
        config_parser['git'] = {
            'main_branch': BRANCH_MAIN,
            'origin_remote': REMOTE_ORIGIN,
            'upstream_remote': REMOTE_UPSTREAM
        }
        config_parser['github'] = {}
        with open(CONFIG_FILE, 'w') as f:
            config_parser.write(f)
    else:
        config_parser.read(CONFIG_FILE)

    ctx.obj = {
        'repo': GitRepo.from_path(path),
        'config': {
            'main_branch': config_parser.get('git', 'main_branch', fallback=BRANCH_MAIN),
            'origin_remote': config_parser.get('git', 'origin_remote', fallback=REMOTE_ORIGIN),
            'upstream_remote': config_parser.get('git', 'upstream_remote', fallback=REMOTE_UPSTREAM),
            'username': config_parser.get('github', 'username', fallback=''),
            'access_token': config_parser.get('github', 'access_token', fallback='')
        }
    }


@bro.command()
@argument('branch')
@option('-s',
        '--since',
        type=str,
        default='master',
        help='Start point of the new branch, default master.')
@click.pass_obj
@error_handler
def pickup(ctx, branch, since):
    '''Start a new branch to work on.'''
    repo, config = ctx['repo'], ctx['config']
    validate_branch(repo, since)

    repo.fetch(config['upstream_remote'], since)
    remote_branch = f'{config["upstream_remote"]}/{since}'
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
def pipeline(ctx, through, merge):
    '''Sync with certain remote branch.'''
    repo, config = ctx['repo'], ctx['config']
    validate_branch(repo, through)

    repo.pull(config['upstream_remote'], through, rebase=not merge)
    method = 'merged' if merge else 'rebased'
    print_normal(f'Synced from {config["upstream_remote"]}/{through} ({method}).')


@bro.command()
@argument('branch')
@option('-k', '--keep-remote', is_flag=True, help='Keep remote branch.')
@click.pass_obj
@error_handler
def putout(ctx, branch, keep_remote):
    '''End the branch after finishing the task.'''
    repo, config = ctx['repo'], ctx['config']
    validate_branch(repo, branch)

    repo.branch_checkout(config['main_branch'])
    print_normal(f'Checked out to branch {config["main_branch"]}.')

    repo.pull(REMOTE_UPSTREAM, BRANCH_MAIN)
    print_normal(f'Synced from remote {config["upstream_remote"]} (rebased).')

    repo.branch_delete(branch)
    print_normal(f'Deleted local branch {branch}.')
    if not keep_remote:
        repo.push(config['origin_remote'], branch, delete=True)
        print_normal(f'Deleted remote branch {config["origin_remote"]}/{branch}.')


@bro.group()
@click.pass_obj
def pull_request(ctx):
    '''Manage pull requests of github.'''
    config = ctx['config']
    if not config['username'] or not config['access_token']:
        username = click.prompt('Please enter github username', type=str)
        password = click.prompt('Please enter github password', hide_input=True, type=str)
        otp_code = click.prompt('Please enter otp code if it is used', default='', hide_input=True, type=str)
        # TODO: 401, 422 等 http error 没有封装
        created, res = request_github_access_token(username, password, otp_code=otp_code)
        if not created:
            print_error(f'Failed to generate access token: {res}')
        else:
            config_parser = ConfigParser()
            config_parser.read(CONFIG_FILE)
            config_parser['github']['username'] = username
            config_parser['github']['access_token'] = res
            with open(CONFIG_FILE, 'w') as f:
                config_parser.write(f)
            print_normal(f'Your access token for gitbro has been generated and saved in {CONFIG_FILE}.')


@pull_request.command()
@argument('owner')
@option('-b', '--base', default='master')
@option('-o', '--open-browser', is_flag=True, help='Display pr on browser.')
@click.pass_obj
def make(ctx, owner, base, open_browser):
    '''Create a pull request.'''
    repo, config = ctx['repo'], ctx['config']
    # Push to remote first.
    repo.push(config['origin_remote'], repo.current_branch)

    title, body = get_pr_msg()
    username, token = config['username'], config['access_token']
    head = f'{username}:{repo.current_branch.name}'
    pr = create_pull_request(
        owner,
        repo.name,
        title,
        head=head,
        base=base,
        auth=(username, token),
        body=body
    )
    print_normal(
        f'Pull request {pr.number} from {head} to {owner}:{base} created.'
    )
    if open_browser:
        try:
            url = pr.extra['urls']['html_url']
            open_new(url)
            print_normal(f'New pull request opened in browser: {url}.')
        except KeyError:
            print_error('Unable to find valid url for new pull request.')


@pull_request.command()
@argument('pr_id')
@argument('branch')
@option('-c', '--checkout', is_flag=True, help='Checkout to the pr branch.')
@click.pass_obj
def get(ctx, pr_id, branch, checkout):
    '''Pull a pull request to local.'''
    repo, config = ctx['repo'], ctx['config']

    remote = config['upstream_remote']
    repo.fetch_pull_request(remote, pr_id, branch)
    print_normal(f'Pulled pr {remote}/{pr_id} to local branch {branch}.')

    if checkout:
        repo.branch_checkout(branch)
        print_normal(f'You are in branch {branch} now.')
