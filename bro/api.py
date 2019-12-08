'''This module defines a thin wrapper class of requests for chaining usage.'''

from logging import getLogger
from os.path import join

from requests.sessions import Session
from requests.auth import HTTPBasicAuth

LOGGER = getLogger(__name__)
DEFAULT_TIMEOUT = 5


class API:
    '''Chaining wrapper class of requests.'''

    def __init__(self, host, timeout=None):
        self.host = host.rstrip('/')
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.paths = []

        self._session = Session()

    def __getattr__(self, key):
        '''Chain up for later url building.'''
        if key:
            self.paths.append(key)
        return self

    def __str__(self):
        return 'RequestApi:<{host}>'.format(host=self.host)

    __repr__ = __str__

    def path(self, *args):
        '''For parameter parts in a url.'''
        for key in args:
            if key:
                self.paths.append(key)
        return self

    def build_url_path(self, append_slash=False):
        '''Build endpoint from host and paths.
        If append_slash is True, an ending slash will be appended
        to the final url.
        '''
        if append_slash:
            self.paths.append('')
        endpoint = join(self.host, *self.paths)

        LOGGER.debug('Built endpoint: %s', endpoint)
        self.paths = []

        return endpoint

    def retrive_response(self,
                         method,
                         url=None,
                         append_slash=False,
                         response_type='json',
                         auth=None,
                         **kwargs):
        '''Actual funtion to make requests and get response.
        Args:
            response_type: type of response to return, could be `text` or `status`, default to `json`.  # noqa
            auth: two items in a tuple, like (username, password)
        Return:
            Depend on response_type, use response.text, response.status_code or response.json().  # noqa
        '''
        if not url:
            url = self.build_url_path(append_slash)
        if auth:
            auth = HTTPBasicAuth(*auth)
        resp = self._session.request(method, url=url, auth=auth, **kwargs)

        LOGGER.debug('Raw response retrived: %s', resp.text)
        resp.raise_for_status()

        if response_type:
            attr = getattr(resp, response_type, None)
            return attr() if callable(attr) else attr

    def get(self,
            headers=None,
            params=None,
            timeout=None,
            auth=None,
            append_slash=False,
            response_type='json'):
        '''Wrapper method of get.'''
        return self.retrive_response('get',
                                     headers=headers,
                                     params=params,
                                     timeout=timeout or self.timeout,
                                     append_slash=append_slash,
                                     response_type=response_type,
                                     auth=auth)

    def post(self,
             headers=None,
             json=None,
             timeout=None,
             auth=None,
             append_slash=False,
             response_type='json'):
        '''Wrapper method of post.'''
        return self.retrive_response('post',
                                     headers=headers,
                                     json=json,
                                     timeout=timeout or self.timeout,
                                     append_slash=append_slash,
                                     response_type=response_type,
                                     auth=auth)

    def put(self,
            headers=None,
            json=None,
            timeout=None,
            auth=None,
            append_slash=False,
            response_type='json'):
        '''Wrapper method of put.'''
        return self.retrive_response('put',
                                     headers=headers,
                                     json=json,
                                     timeout=timeout or self.timeout,
                                     append_slash=append_slash,
                                     response_type=response_type,
                                     auth=auth)

    def patch(self,
              headers=None,
              json=None,
              timeout=None,
              auth=None,
              append_slash=False,
              response_type='json'):
        '''Wrapper method of patch.'''
        return self.retrive_response('patch',
                                     headers=headers,
                                     json=json,
                                     timeout=timeout or self.timeout,
                                     append_slash=append_slash,
                                     response_type=response_type,
                                     auth=auth)

    def delete(self,
               headers=None,
               json=None,
               timeout=None,
               auth=None,
               append_slash=False,
               response_type='json'):
        '''Wrapper method of delete.'''
        return self.retrive_response('delete',
                                     headers=headers,
                                     json=json,
                                     timeout=timeout or self.timeout,
                                     append_slash=append_slash,
                                     response_type=response_type,
                                     auth=auth)
