import abc
import getpass
import hashlib
import sys


class SSHConfigApplication(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, api, ssh_config, cryptor, logger):
        self._api = api
        self._config = ssh_config
        self._cryptor = cryptor
        self._logger = logger

        self._hosts = None
        self._full_hosts = None

        self._sa_username = None
        self._sa_master_password = None
        self._sa_auth_key = None

        self._sa_keys = None
        self._sa_connections = None
        return

    @abc.abstractmethod
    def run(self):
        pass

    def _valediction(self):
        self._logger.log("Bye!", color='magenta')
        return

    def _get_sa_user(self):
        def hash_password(password):
            return hashlib.sha256(password).hexdigest()

        self._sa_username = raw_input("Enter your Server Auditor's username: ").strip()
        self._sa_master_password = getpass.getpass("Enter your Server Auditor's password: ")
        password = hash_password(self._sa_master_password)
        try:
            self._sa_auth_key = self._api.get_auth_key(self._sa_username, password)
        except Exception as exc:
            self._logger.log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._logger.log("Success!", color='green')
        return

    def _get_sa_keys_and_connections(self):
        self._logger.log("Getting current keys and connections...")

        try:
            keys, self._sa_connections = self._api.get_keys_and_connections(self._sa_username, self._sa_auth_key)
        except Exception as exc:
            self._logger.log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._sa_keys = {}
        for key in keys:
            self._sa_keys[key['id']] = key

        self._logger.log("Success!", color='green')
        return

    def _decrypt_sa_keys_and_connections(self):
        self._logger.log("Decrypting keys and connections...")

        # TODO: looks like good for multiprocessing
        try:
            for key, value in self._sa_keys.items():
                #value['label'] = self._cryptor.decrypt(value['label'], self._sa_master_password)
                #value['passphrase'] = self._cryptor.decrypt(value['passphrase'], self._sa_master_password)
                value['private_key'] = self._cryptor.decrypt(value['private_key'], self._sa_master_password)
                #value['public_key'] = self._cryptor.decrypt(value['public_key'], self._sa_master_password)

            for con in self._sa_connections:
                #con['label'] = self._cryptor.decrypt(con['label'], self._sa_master_password)
                con['hostname'] = self._cryptor.decrypt(con['hostname'], self._sa_master_password)
                con['ssh_username'] = self._cryptor.decrypt(con['ssh_username'], self._sa_master_password)
                #con['ssh_password'] = self._cryptor.decrypt(con['ssh_password'], self._sa_master_password)
        except Exception as exc:
            self._logger.log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._logger.log("Success!", color='green')
        return

    def _parse_local_config(self):
        self._logger.log("Parsing ssh config file...")

        try:
            self._config.parse()
        except Exception as exc:
            self._logger.log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._hosts = self._config.get_complete_hosts()

        self._logger.log("Success!", color='green')
        return