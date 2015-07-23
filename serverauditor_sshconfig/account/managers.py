# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

from ..core.api import API


class AccountManager(object):

    def __init__(self, config):
        self.config = config
        self.api = API()

    def login(self, username, password):
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
        self.config.remove_section('User')
        self.config.write()
