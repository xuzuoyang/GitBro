import logging
import requests
from os.path import join

LOGGER = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 3


class API:
    """Wrapper for requests"""

    def __init__(self, url, timeout=None):
        self.url = url
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.paths = []

        self._session = requests.Session()

    def __getattr__(self, key):
        if key:
            self.paths.append(key)
        return self

    def __str__(self):
        return 'RequestApi:<{url}>'.format(url=self.url)

    __repr__ = __str__

    def path(self, *args):
        for key in args:
            if key:
                self.paths.append(key)
        return self

    def build_url_path(self, append_slash=True):
        """Build endpoint from base url and paths."""
        if append_slash:
            self.paths.append('/')
        endpoint = join(
            '{base_url}/'.format(base_url=self.url.rstrip('/')),
            '/'.join(self.paths).lstrip('/')
        )

        self.paths = []
        return endpoint

    def retrive_response(self, method, headers=None, json=None, timeout=None, append_slash=True, response_type='json', **kwargs):
        '''Actual funtion to make request and get response.'''
        resp = self._session.request(
            method,
            url=self.build_url_path(append_slash),
            headers=headers,
            json=json,
            timeout=timeout or self.timeout,
            **kwargs
        )

        resp.raise_for_status()

        if response_type:
            attr = getattr(resp, response_type, None)
            return attr() if callable(attr) else attr

    def get(self, headers=None, params=None, append_slash=True, response_type='json'):
        return self.retrive_response(
            'get',
            headers=headers,
            params=params,
            append_slash=append_slash,
            response_type=response_type
        )

    def post(self, headers=None, json=None, append_slash=True):
        pass

    def head(self, headers=None, json=None, append_slash=True):
        pass

    def put(self, headers=None, json=None, append_slash=True):
        pass

    def patch(self, headers=None, json=None, append_slash=True):
        pass

    def delete(self, headers=None, json=None, append_slash=True):
        pass
