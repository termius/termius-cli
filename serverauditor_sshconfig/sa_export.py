#!/usr/bin/env python
# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import sys

from serverauditor_sshconfig.core.application import SSHConfigApplication, description
from serverauditor_sshconfig.core.api import API
from serverauditor_sshconfig.core.cryptor import RNCryptor
from serverauditor_sshconfig.core.logger import PrettyLogger
from serverauditor_sshconfig.core.ssh_config import SSHConfig
from serverauditor_sshconfig.core.utils import p_input, p_map


class ExportSSHConfigApplication(SSHConfigApplication):

    def run(self):
        self._greeting()

        self._get_sa_user()
        self._get_sa_keys_and_connections()
        self._decrypt_sa_keys_and_connections()

        self._parse_local_config()
        self._sync_for_export()
        self._choose_new_hosts()
        self._get_full_hosts()

        self._create_keys_and_connections()

        self._valediction()
        return

    def _greeting(self):
        self._logger.log("ServerAuditor's ssh config script. Export from your computer to SA account.", color='magenta')
        return

    @description("Synchronization...")
    def _sync_for_export(self):
        def get_identity_files(host):
            return [f[1] for f in host.get('identityfile', [])]

        def is_exist(host):
            h = self._config.get_host(host, substitute=True)
            has_key = bool(h.get('identityfile', None))
            for conn in self._sa_connections:
                key_check = True
                key_id = conn['ssh_key']
                if has_key:
                    if key_id:
                        key_check = self._sa_keys[key_id['id']]['private_key'] in get_identity_files(h)
                    else:
                        continue
                else:
                    if key_id:
                        continue

                if (conn['hostname'] == h['hostname'] and
                        conn['ssh_username'] == h['user'] and
                        conn['port'] == int(h.get('port', 22)) and
                        key_check):  # conn['label'] == h['host']
                    return True

            return False

        for host in self._local_hosts[:]:
            if is_exist(host):
                self._local_hosts.remove(host)

        return

    def _choose_new_hosts(self):
        def get_prompt():
            if self._local_hosts:
                return "You may confirm this list (press 'Enter'), add (enter '+') or remove (enter its number) host: "
            else:
                return "You may confirm this list (press 'Enter') or add (enter '+') host: "

        def get_hosts_names():
            return ', '.join('%s (#%d)' % (h, i) for i, h in enumerate(self._local_hosts)) or '[]'

        self._logger.log("The following new hosts have been founded in your ssh config:", sleep=0)
        self._logger.log(get_hosts_names(), color='blue')

        while True:
            number = p_input(get_prompt()).strip()

            if number == '':
                break

            if number == '+':
                host = p_input("Enter host: ")
                conf = self._config.get_host(host)
                if list(conf.keys()) == ['host']:
                    self._logger.log("There is no config for host %s!" % host, color='red', file=sys.stderr)
                else:
                    self._local_hosts.append(host)

            else:
                try:
                    number = int(number)
                    if number >= len(self._local_hosts) or number < 0:
                        raise IndexError
                except (ValueError, IndexError):
                    self._logger.log("Incorrect index!", color='red', file=sys.stderr)
                    continue
                else:
                    self._local_hosts.pop(number)

            self._logger.log(get_hosts_names(), color='blue')

        self._logger.log("Ok!", color='green')
        if not self._local_hosts:
            self._valediction()
            sys.exit(0)
        return

    @description("Getting full information...")
    def _get_full_hosts(self):
        def check_duplicates(hosts):
            new_hosts = []
            new_hosts_ids = set()
            new_hosts_names = {}
            for host in hosts:
                host_id = '{host[user]}@{host[hostname]}:{host[port]}'.format(host=host)
                if not host_id in new_hosts_ids:
                    new_hosts_ids.add(host_id)
                    new_hosts.append(host)
                    new_hosts_names[host_id] = host['host']
                else:
                    self._logger.log('Seems "{cur_host}" is an duplicate of "{ex_host}"!'.format(
                        cur_host=host['host'],
                        ex_host=new_hosts_names[host_id]
                    ), color='blue')
            return new_hosts

        def encrypt_host(host):
            host['host'] = self._cryptor.encrypt(host['host'], self._sa_master_password)
            host['hostname'] = self._cryptor.encrypt(host['hostname'], self._sa_master_password)
            host['user'] = self._cryptor.encrypt(host['user'], self._sa_master_password)
            host['password'] = ''

            host['ssh_key'] = []
            for i, f in enumerate(host.get('identityfile', [])):
                ssh_key = {
                    'label': self._cryptor.encrypt(f[0], self._sa_master_password),
                    'private_key': self._cryptor.encrypt(f[1], self._sa_master_password),
                    'public_key': '',
                    'passphrase': ''
                }
                host['ssh_key'].append(ssh_key)
            return host

        almost_full_local_hosts = [self._config.get_host(h, substitute=True) for h in self._local_hosts]
        full_local_hosts = check_duplicates(almost_full_local_hosts)
        self._full_local_hosts = p_map(encrypt_host, full_local_hosts)
        return

    @description("Creating keys and connections...")
    def _create_keys_and_connections(self):
        self._api.create_keys_and_connections(self._full_local_hosts, self._sa_username, self._sa_auth_key)
        return


def main():
    app = ExportSSHConfigApplication(api=API(), ssh_config=SSHConfig(), cryptor=RNCryptor(), logger=PrettyLogger())
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        sys.exit(1)
    return

if __name__ == "__main__":

    main()