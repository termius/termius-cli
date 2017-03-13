# -*- coding: utf-8 -*-
"""Module with Account manager."""
import uuid

from six.moves import configparser
from ..core.api import API
from ..core.exceptions import OptionNotSetException


class AccountManager(object):
    """Class to keep logic for login and logout."""

    setting_names = ('synchronize_key', 'agent_forwarding')

    def __init__(self, config):
        """Create new account manager."""
        self.config = config
        self.api = API()

    def login(self, username, password, authy_token=None):
        """Retrieve apikey and crypto settings from server."""
        response = self.api.login(username, password, authy_token)
        self.config.set('User', 'username', username)
        apikey = response['token']
        self.config.set('User', 'apikey', apikey)
        hmac_salt = response['hmac_salt']
        self.config.set('User', 'hmac_salt', hmac_salt)
        salt = response['salt']
        self.config.set('User', 'salt', salt)
        self.config.write()

    def set_settings(self, dictionary):
        """Store settings."""
        filtered_settings = {
            k: (dictionary[k] and 'yes') or 'no' for k in self.setting_names
        }
        for k, i in filtered_settings.items():
            self.config.set('Settings', k, i)
        self.config.write()

    def get_settings(self):
        """Get settings or return default."""
        return {
            i: self.config.get_safe('Settings', i, default='yes') == 'yes'
            for i in self.setting_names
        }

    def logout(self):
        """Remove apikey and other credentials."""
        self.config.remove_section('User')
        self.config.remove_section('Settings')
        self.config.remove_section('CloudSynchronization')
        self.config.write()

    @property
    def analytics_id(self):
        """Get or create analytics id for device."""
        try:
            client_id = self.config.get('User', 'analytics_id')
        except (configparser.NoSectionError, configparser.NoOptionError):
            client_id = uuid.uuid4()

            self.config.set('User', 'analytics_id', client_id)
            self.config.write()

        return client_id

    @property
    def username(self):
        """Get username."""
        try:
            return self.config.get('User', 'username')
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise OptionNotSetException
