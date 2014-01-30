#!/usr/bin/env python
# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import os
import stat
import sys

from serverauditor_sshconfig.core.application import SSHConfigApplication, description
from serverauditor_sshconfig.core.api import API
from serverauditor_sshconfig.core.cryptor import RNCryptor
from serverauditor_sshconfig.core.logger import PrettyLogger
from serverauditor_sshconfig.core.ssh_config import SSHConfig
from serverauditor_sshconfig.core.utils import p_input


class ImportSSHConfigApplication(SSHConfigApplication):

    SSH_KEYS_DIR = '~/.ssh/serverauditor/'
    SSH_CONFIG_HOST_TEMPLATE = """\
# The following host was created by ServerAuditor
Host {host}
    User {user}
    HostName {hostname}
    Port {port}
"""
    SSH_CONFIG_HOST_IDENTITY_FILE = """\
    IdentityFile {key}
"""
    SSH_CONFIG_HOST_DUPLICATE = """\
# Duplicate host will not work with SSH
"""

    def run(self):
        self._greeting()

        self._get_sa_user()
        self._get_sa_keys_and_connections()
        self._decrypt_sa_keys_and_connections()
        self._fix_sa_keys_and_connections()

        self._parse_local_config()
        self._sync_for_import()
        self._choose_new_hosts()
        self._create_keys_and_connections()

        self._valediction()
        return

    def _greeting(self):
        self._logger.log("ServerAuditor's ssh config script. Import from SA account to your computer.", color='magenta')
        return

    @description("Synchronization...")
    def _sync_for_import(self):
        def get_identity_files(host):
            return [f[1] for f in host.get('identityfile', [])]

        def is_exist(conn):
            attempt = conn['label'] or conn['hostname']
            h = self._config.get_host(attempt, substitute=True)
            key_check = True
            key_id = conn['ssh_key']
            if key_id:
                key_check = self._sa_keys[key_id['id']]['private_key'] in get_identity_files(h)
            return (conn['ssh_username'] == h['user'] and
                    conn['hostname'] == h['hostname'] and
                    conn['port'] == h['port'] and
                    key_check)

        for conn in self._sa_connections[:]:
            if is_exist(conn):
                name = conn['label'] or "%s@%s:%s" % (conn['ssh_username'], conn['hostname'], conn['port'])
                self._logger.log('Connection "%s" can already be used by ssh.' % name, color='blue')
                self._sa_connections.remove(conn)

        return

    @description(valediction="OK!")
    def _choose_new_hosts(self):
        def get_connection_name(conn, number):
            name = self._get_sa_connection_name(conn)
            return '%s (#%d)' % (name, number)

        def get_connections_names():
            return (', '.join(get_connection_name(c, i) for i, c in enumerate(self._sa_connections))
                    or 'There are no more connections!')

        if not self._sa_connections:
            self._logger.log("There are no new connections on ServerAuditor's servers.")
            self._valediction()
            sys.exit(0)

        self._logger.log("The following new hosts have been founded on ServerAuditor's servers:", sleep=0)
        self._logger.log(get_connections_names(), color='blue')

        prompt = "You may confirm this list (press 'Enter') or remove host (enter its number): "
        while len(self._sa_connections):
            number = p_input(prompt).strip()

            if number == '':
                break

            try:
                number = int(number)
                if number >= len(self._sa_connections) or number < 0:
                    raise IndexError
            except (ValueError, IndexError):
                self._logger.log("Incorrect index!", color='red', file=sys.stderr)
            else:
                self._sa_connections.pop(number)
                self._logger.log(get_connections_names(), color='blue')

        if not self._sa_connections:
            self._valediction()
            sys.exit(0)
        return

    @description("Creating keys and connections...")
    def _create_keys_and_connections(self):
        def get_param_name(s):
            if any(c.isspace() for c in s):
                return '"%s"' % s
            return s

        def check_ssh_keys_dir():
            key_dir = os.path.expanduser(self.SSH_KEYS_DIR)
            if not os.path.exists(key_dir):
                os.mkdir(key_dir)

        def get_key_path(key):
            key_name = test_key_name = os.path.join(self.SSH_KEYS_DIR, key['label'])
            i = 1
            while os.path.exists(os.path.expanduser(test_key_name)):
                test_key_name = key_name + '-%d' % i
                i += 1
            return test_key_name

        def create_connection(conn):

            name = conn['label'] or conn['hostname']
            is_duplicate = name in self._local_hosts
            if is_duplicate:
                self._logger.log(('Seems local config already contains host with name "{name}". '
                                  'SSH won\'t be able to use the second one.').format(name=name), color='blue')

            with open(self._config.USER_CONFIG_PATH, 'a') as cf:
                if is_duplicate:
                    cf.write(self.SSH_CONFIG_HOST_DUPLICATE)

                host = self.SSH_CONFIG_HOST_TEMPLATE.format(
                    host=get_param_name(name),
                    hostname=get_param_name(conn['hostname']),
                    user=get_param_name(conn['ssh_username']),
                    port=conn['port']
                )
                cf.write(host)

                if conn['ssh_key']:
                    key = self._sa_keys[conn['ssh_key']['id']]
                    key_name = get_key_path(key)
                    idf = self.SSH_CONFIG_HOST_IDENTITY_FILE.format(key=get_param_name(key_name))
                    cf.write(idf)

                cf.write('\n')

            if conn['ssh_key']:
                check_ssh_keys_dir()
                key = self._sa_keys[conn['ssh_key']['id']]
                key_name = os.path.expanduser(get_key_path(key))

                if key['private_key']:
                    with open(key_name, 'w') as private_file:
                        private_file.write(key['private_key'])
                    os.chmod(key_name, stat.S_IWUSR | stat.S_IRUSR)

                if key['public_key']:
                    with open(key_name + '.pub', 'w') as public_file:
                        public_file.write(key['public_key'])
                    os.chmod(key_name + '.pub', stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

            return

        for conn in self._sa_connections:
            create_connection(conn)

        return


def main():
    app = ImportSSHConfigApplication(api=API(), ssh_config=SSHConfig(), cryptor=RNCryptor(), logger=PrettyLogger())
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        sys.exit(1)
    return


if __name__ == "__main__":

    main()
