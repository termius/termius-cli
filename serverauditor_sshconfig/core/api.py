# -*- coding: utf-8 -*-
"""Package with api client."""
import logging
import hashlib
import six
import requests
from requests.auth import AuthBase


# pylint: disable=too-few-public-methods
class ServerauditorAuth(AuthBase):
    """Authentication method to sync-cloud."""

    header_name = 'Authorization'

    def __init__(self, username, apikey):
        """Create new authenticator."""
        self.username = username
        self.apikey = apikey

    @property
    def auth_header(self):
        """Render auth header content."""
        return 'ApiKey {username}:{apikey}'.format(
            username=self.username, apikey=self.apikey
        )

    def __call__(self, request):
        """Add header to request."""
        request.headers[self.header_name] = self.auth_header
        return request


def hash_password(password):
    """Generate hash from password."""
    password = six.b(password)
    return hashlib.sha256(password).hexdigest()


class API(object):
    """Class to send requests to sync cloud."""

    host = 'serverauditor.com'
    base_url = 'https://{}/api/'.format(host)
    logger = logging.getLogger(__name__)

    def __init__(self, username=None, apikey=None):
        """Construct new API instance."""
        if username and apikey:
            self.auth = ServerauditorAuth(username, apikey)
        else:
            self.auth = None

    def set_auth(self, username, apikey):
        """Provide credentials."""
        self.auth = ServerauditorAuth(username, apikey)

    def request_url(self, endpoint):
        """Create full url to endpoint."""
        return self.base_url + endpoint

    def login(self, username, password):
        """Return user's auth token."""
        password = hash_password(password)
        response = requests.get(self.request_url('v1/token/auth/'),
                                auth=(username, password))
        if response.status_code != 200:
            self.logger.warning('Can not login!\nResponse %s', response.text)
        assert response.status_code == 200

        response_payload = response.json()
        apikey = response_payload['key']
        self.set_auth(username, apikey)
        return response_payload

    def post(self, endpoint, data):
        """Send authorized post request."""
        response = requests.post(self.request_url(endpoint),
                                 json=data, auth=self.auth)
        assert response.status_code == 201, response.text
        return response.json()

    def get(self, endpoint):
        """Send authorized get request."""
        response = requests.get(self.request_url(endpoint), auth=self.auth)
        assert response.status_code == 200, response.text
        return response.json()

    def delete(self, endpoint):
        """Send authorized delete request."""
        response = requests.delete(self.request_url(endpoint), auth=self.auth)
        assert response.status_code in (200, 204)
        return response.json()

    def put(self, endpoint, data):
        """Send authorized put request."""
        response = requests.put(self.request_url(endpoint),
                                json=data, auth=self.auth)
        assert response.status_code in (200, 202), response.text
        return response.json()
