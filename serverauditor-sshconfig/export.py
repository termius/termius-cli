#!/usr/bin/env python
#
# Copyright 2013 Crystalnix
#
# License will be here.

""" Short description.

Verbose description. Verbose description. Verbose description.
Verbose description. Verbose description. Verbose description.
Verbose description.

Useful links:
http://www.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3

TODO: Create tests.
TODO: Create and handle exceptions.
TODO: Check on python 2.4-7, 3.0-4 (see tox).
"""


from __future__ import print_function, with_statement

import getpass
import hashlib
import pprint
import sys
import time

from core.api import API
from core.cryptor import RNCryptor
from core.ssh_config import SSHConfig


class ExportApplication(object):

    COLOR_END = '\033[0m'
    COLOR_BOLD = '\033[1m'
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'end': COLOR_END
    }

    def __init__(self, ssh_config, api, cryptor):
        self._config = ssh_config
        self._api = api
        self._cryptor = cryptor

        self._hosts = None
        self._full_hosts = None

        self._sa_username = None
        self._sa_master_password = None
        self._sa_auth_key = None

        self._sa_keys = None
        self._sa_connections = None
        return

    def run(self):
        self._greeting()
        self._get_sa_user()
        self._get_keys_and_connections()
        self._decrypt_keys_and_connections()
        self._parse_config()
        self._sync()
        self._get_hosts()
        self._get_full_hosts()
        self._create_keys_and_connections()
        return

    def _log(self, message, is_pprint=False, sleep=0.5, color='end', color_bold=False, *args, **kwargs):
        print(self.COLORS.get(color, self.COLOR_END), end='')
        if color_bold:
            print(self.COLOR_BOLD, end='')
        if is_pprint:
            pprint.pprint(message, *args, **kwargs)
        else:
            print(message, end='', *args, **kwargs)
        print(self.COLOR_END)
        if sleep:
            time.sleep(sleep)
        return

    def _greeting(self):
        self._log("ServerAuditor's ssh config script.", color='magenta')
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
            self._log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._log("Success!", color='green')
        return

    def _get_keys_and_connections(self):
        self._log("Getting current keys and connections...")

        try:
            keys, self._sa_connections = self._api.get_keys_and_connections(self._sa_username, self._sa_auth_key)
        except Exception as exc:
            self._log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._sa_keys = {}
        for key in keys:
            self._sa_keys[key['id']] = key

        self._log("Success!", color='green')
        return

    def _decrypt_keys_and_connections(self):
        self._log("Decrypting keys and connections...")

        try:
            for key, value in self._sa_keys.items():
                value['label'] = self._cryptor.decrypt(value['label'], self._sa_master_password)
                value['passphrase'] = self._cryptor.decrypt(value['passphrase'], self._sa_master_password)
                value['private_key'] = self._cryptor.decrypt(value['private_key'], self._sa_master_password)
                value['public_key'] = self._cryptor.decrypt(value['public_key'], self._sa_master_password)

            for con in self._sa_connections:
                con['label'] = self._cryptor.decrypt(con['label'], self._sa_master_password)
                con['hostname'] = self._cryptor.decrypt(con['hostname'], self._sa_master_password)
                con['ssh_username'] = self._cryptor.decrypt(con['ssh_username'], self._sa_master_password)
                con['ssh_password'] = self._cryptor.decrypt(con['ssh_password'], self._sa_master_password)
        except Exception as exc:
            self._log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._log("Success!", color='green')
        return

    def _parse_config(self):
        self._log("Parsing ssh config file...")

        try:
            self._config.parse()
        except Exception as exc:
            self._log("Error! %s" % exc, file=sys.stderr, color='red')
            sys.exit(1)

        self._hosts = self._config.get_complete_hosts()

        self._log("Success!", color='green')
        return

    def _sync(self):
        def is_exist(host):
            h = self._config.get_host(host, substitute=True)
            for conn in self._sa_connections:
                key_id = conn['ssh_key']
                if (#key_id and
                        conn['hostname'] == h['hostname'] and
                        #conn['label'] == h['host'] and
                        conn['ssh_username'] == h['user'] # and
                        #self._sa_keys[key_id['id']]['value'] == h['identityfile']
                        ):
                    return True
            return False

        self._log("Synchronization...")

        for host in self._hosts[:]:
            if is_exist(host):
                self._hosts.remove(host)

        self._log("Success!", color='green')
        return

    def _get_hosts(self):
        self._log("The following new hosts have been founded in your ssh config:")
        self._log(self._hosts)
        number = None
        while number != '=':
            number = raw_input("You may confirm this list (press '='), "
                               "add new host (press '+') or "
                               "remove host (press '-'): ").strip()
            if number == '+':
                host = raw_input("Adding host: ")
                conf = self._config.get_host(host)
                if conf.keys() == ['host']:
                    self._log("There is no config for host %s!" % host, file=sys.stderr)
                else:
                    self._hosts.append(host)

                self._log("Hosts:\n%s" % self._hosts)

            elif number == '-':
                host = raw_input("Deleting host: ")
                if host in self._hosts:
                    self._hosts.remove(host)
                else:
                    self._log("There is no host %s!" % host, file=sys.stderr)

                self._log("Hosts:\n%s" % self._hosts)

        self._log("Ok!", color='green')
        return

    def _get_full_hosts(self):
        def encrypt_host(host):
            host['host'] = self._cryptor.encrypt(host['host'], self._sa_master_password)
            host['hostname'] = self._cryptor.encrypt(host['hostname'], self._sa_master_password)
            host['user'] = self._cryptor.encrypt(host['user'], self._sa_master_password)
            host['password'] = self._cryptor.encrypt('', self._sa_master_password)
            return host

        self._log("Getting full information...")
        self._full_hosts = [encrypt_host(self._config.get_host(h, substitute=True)) for h in self._hosts]

        self._log("Success!", color='green')
        return

    def _create_keys_and_connections(self):
        self._log("Creating keys and connections...")
        try:
            self._api.create_keys_and_connections(self._full_hosts, self._sa_username, self._sa_auth_key)
        except Exception as exc:
            self._log("Error! %s" % exc, file=sys.stderr)
            sys.exit(1)

        self._log("Success!", color='green')
        return


def main():
    app = ExportApplication(ssh_config=SSHConfig(), api=API(), cryptor=RNCryptor())
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        pass
    print("\nBye!")
    return


if __name__ == "__main__":

    main()