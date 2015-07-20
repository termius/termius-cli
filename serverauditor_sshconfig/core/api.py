# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import requests
from requests.auth import AuthBase


class ServerauditorAuth(AuthBase):

    def __init__(self, username, apikey):
        self.username = username
        self.apikey = apikey

    @property
    def auth_header(self):
        return "ApiKey {username}:{apikey}".format(
            username=username, apikey=apikey
        )

    def __call__(self, request):
        request.headers['Authorization'] = self.auth_header
        return request


class API(object):

    host = 'serverauditor.com'
    base_url = 'https://{}/api/'.format(host)

    def __init__(self, username=None, apikey=None):
        if username and apikey:
            self.auth = ServerauditorAuth(username, apikey)
        else:
            self.auth = None

    def set_auth(self, username, apikey):
        self.auth = ServerauditorAuth(username, apikey)

    def request_url(self, endpoint):
        return self.base_url + endpoint

    def login(self, username, password):
        """Returns user's auth token."""
        response = requests.get(self.request_url("token/auth/"),
                               auth=(username, password))
        assert response.status_code == 200

        response_payload = response.json()
        apikey = response_payload.pop('key')
        self.set_auth(username, apikey)
        return response_payload
