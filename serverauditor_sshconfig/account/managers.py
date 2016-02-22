# -*- coding: utf-8 -*-
"""Module with Account manager."""
from six.moves import configparser
from ..core.api import API
from ..core.exceptions import OptionNotSetException


class AccountManager(object):
    """Class to keep logic for login and logout."""

    def __init__(self, config):
        """Create new account manager."""
        self.config = config
        self.api = API()

    def login(self, username, password):
        """Retrieve apikey and crypto settings from server."""
        response = self.api.login(username, password)
        self.config.set('User', 'username', username)
        apikey = response['key']
        self.config.set('User', 'apikey', apikey)
        hmac_salt = response['hmac_salt']
        self.config.set('User', 'hmac_salt', hmac_salt)
        salt = response['salt']
        self.config.set('User', 'salt', salt)
        self.config.write()

    def logout(self):
        """Remove apikey and other credentials."""
        self.config.remove_section('User')
        self.config.write()

    @property
    def username(self):
        """Get username."""
        try:
            return self.config.get('User', 'username')
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise OptionNotSetException
