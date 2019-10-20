'''
This module provides a class and all the management functions of pull request.
'''

from logging import getLogger

from .api import API

LOGGER = getLogger(__name__)
GITHUB_API = API('https://api.github.com')
GITHUB_PATCH_API = API('https://patch-diff.githubusercontent.com')


class PullRequest:
    '''Pull request object.
    Divides a pull request into 3 parts: metadata, main content and extra info.
    '''

    @classmethod
    def from_json(cls, **kwargs):
        '''Create an object from json data.'''
        return cls(**kwargs)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def meta(self):
        return {
            'id': getattr(self, 'id', -1),
            # 'node_id': getattr(self, 'node_id', ''),
            'number': getattr(self, 'number', -1),
            'base': getattr(self, 'base', {})['label'],
            'head': getattr(self, 'head', {})['label'],
            'state': getattr(self, 'state', ''),
            'merged': getattr(self, 'merged', None),
            'mergeable': getattr(self, 'mergeable', None),
            # 'rebaseable': getattr(self, 'rebaseable', None),
            'created_at': getattr(self, 'created_at', ''),
            'updated_at': getattr(self, 'updated_at', ''),
            'closed_at': getattr(self, 'closed_at', ''),
            'merged_at': getattr(self, 'merged_at', ''),
        }

    @property
    def content(self):
        return {
            'title':
            getattr(self, 'title', ''),
            'body':
            getattr(self, 'body', ''),
            'commits':
            getattr(self, 'commits', -1),
            'additions':
            getattr(self, 'additions', -1),
            'deletions':
            getattr(self, 'deletions', -1),
            'changed_files':
            getattr(self, 'changed_files', -1),

            # 'assignee': getattr(self, 'assignee', None),
            # 'assignees': getattr(self, 'assignees', None) or '',
            'requested_reviewers':
            getattr(self, 'requested_reviewers', None) or '',

            # 'labels': getattr(self, 'labels', None) or '',
            # 'milestone': getattr(self, 'milestone', None)
        }

    @property
    def extra(self):
        return {
            'author': getattr(self, 'user', {}),
            'urls': {
                'html_url': getattr(self, 'html_url', ''),
                'diff_url': getattr(self, 'diff_url', ''),
                'patch_url': getattr(self, 'patch_url', ''),
                'comments_url': getattr(self, 'comments_url', ''),
                'review_comments_url': getattr(self, 'review_comments_url',
                                               ''),
            }
        }


def create_pull_request(owner,
                        repo,
                        title,
                        head,
                        base,
                        auth,
                        body='',
                        mcm=False,
                        issue=None):
    payload = {'head': head, 'base': base}
    if issue:
        payload['issue'] = issue
    else:
        payload['title'] = title
        payload['body'] = body

    json_resp = GITHUB_API.repos.path(owner, repo).pulls.post(json=payload,
                                                              auth=auth)
    pull_request = PullRequest.from_json(**json_resp)
    return pull_request


def get_pull_request(owner, repo, number, patch=False):
    if patch:
        return GITHUB_PATCH_API.raw.path(owner, repo).pull.path(
            '%s.diff' % number).get(response_type='text')

    json_resp = GITHUB_API.repos.path(owner, repo).pulls.path(number).get()
    pull_request = PullRequest.from_json(**json_resp)
    return pull_request


def comment_pull_request(owner, repo, number, auth, comment):
    ''''''
    payload = {'body': comment}
    json_resp = GITHUB_API.repos.path(
        owner, repo).issues.path(number).comments.post(json=payload, auth=auth)
    return json_resp


def update_pull_request(owner, repo, number, auth, **payload):
    '''
    Args:
        kwargs:
            title: Title of the pull request.
            body: Body of the pull request.
            state: Should be either `open` or `closed`.
            mcm: If maintainers can modify the pr.
    '''
    json_resp = GITHUB_API.repos.path(owner, repo).pulls.path(number).patch(
        json=payload, auth=auth)
    pull_request = PullRequest.from_json(**json_resp)
    return pull_request


def merge_pull_request(owner, repo, number, auth, **payload):
    '''
    Args:
        kwargs:
            commit_message: Message for the merge commit.
    '''
    json_resp = GITHUB_API.repos.path(
        owner, repo).pulls.path(number).merge.put(json=payload, auth=auth)
    return json_resp
