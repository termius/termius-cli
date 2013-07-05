import abc
import base64
import ConfigParser
import functools
import getpass
import hashlib
import os
import sys

from .utils import parallel_map


def description(message):

    def decorator(func):

        @functools.wraps(func)
        def wrapped(self):
            if message:
                self._logger.log(message)
            try:
                func(self)
            except Exception as exc:
                self._logger.log("Error! %s" % exc, file=sys.stderr, color='red')
                sys.exit(1)

            self._logger.log("Success!", color='green')
            return

        return wrapped

    return decorator


class SSHConfigApplication(object):
    __metaclass__ = abc.ABCMeta

    SERVER_AUDITOR_SETTINGS_PATH = os.path.expanduser('~/.serverauditor')

    def __init__(self, api, ssh_config, cryptor, logger):
        self._api = api
        self._config = ssh_config
        self._cryptor = cryptor
        self._logger = logger

        self._sa_username = None
        self._sa_master_password = None
        self._sa_auth_key = None

        self._sa_keys = None
        self._sa_connections = None

        self._local_hosts = None
        self._full_local_hosts = None
        return

    @abc.abstractmethod
    def run(self):
        pass

    def _valediction(self):
        self._logger.log("Bye!", color='magenta')
        return

    @description(None)
    def _get_sa_user(self):
        def hash_password(password):
            return hashlib.sha256(password).hexdigest()

        def read_name_from_config():
            settings_path = self.SERVER_AUDITOR_SETTINGS_PATH
            if not os.path.exists(settings_path):
                with open(settings_path, 'w+'):
                    pass
                return None
            settings = ConfigParser.ConfigParser()
            settings.read([settings_path])
            return settings.get('User', 'name')

        def write_name_to_config(name):
            settings = ConfigParser.ConfigParser()
            settings.add_section('User')
            settings.set('User', 'name', name)
            with open(self.SERVER_AUDITOR_SETTINGS_PATH, 'w') as f:
                settings.write(f)
            return

        prompt = "Enter your Server Auditor's username%s: "
        name = read_name_from_config()
        if name:
            prompt %= (' [%s]' % name)
            self._sa_username = raw_input(prompt).strip() or name
        else:
            prompt %= ''
            self._sa_username = raw_input(prompt).strip()

        write_name_to_config(self._sa_username)
        self._sa_master_password = getpass.getpass("Enter your Server Auditor's password: ")
        data = self._api.get_auth_key(self._sa_username, hash_password(self._sa_master_password))
        self._sa_auth_key = data['key']
        self._cryptor.iv = base64.decodestring(data['iv'])
        self._cryptor.encryption_salt = base64.decodestring(data['salt'])
        return

    @description("Getting current keys and connections...")
    def _get_sa_keys_and_connections(self):
        keys, self._sa_connections = self._api.get_keys_and_connections(self._sa_username, self._sa_auth_key)
        self._sa_keys = {}
        for key in keys:
            self._sa_keys[key['id']] = key

        return

    @description("Decrypting keys and connections...")
    def _decrypt_sa_keys_and_connections(self):
        def decrypt_key(kv):
            key = kv[0]
            value = kv[1]
            value = {
                'label': self._cryptor.decrypt(value['label'], self._sa_master_password),
                'private_key': self._cryptor.decrypt(value['private_key'], self._sa_master_password),
                'public_key': self._cryptor.decrypt(value['public_key'], self._sa_master_password),
            }
            return key, value

        def decrypt_connection(con):
            con['label'] = self._cryptor.decrypt(con['label'], self._sa_master_password)
            con['hostname'] = self._cryptor.decrypt(con['hostname'], self._sa_master_password)
            con['ssh_username'] = self._cryptor.decrypt(con['ssh_username'], self._sa_master_password)
            return con

        self._sa_keys = dict(parallel_map(decrypt_key, self._sa_keys.items()))
        self._sa_connections = parallel_map(decrypt_connection, self._sa_connections)

        return

    @description("Parsing ssh config file...")
    def _parse_local_config(self):
        self._config.parse()
        self._local_hosts = self._config.get_complete_hosts()
        return