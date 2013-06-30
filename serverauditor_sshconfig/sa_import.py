#!/usr/bin/env python
#
# Copyright 2013 Crystalnix

import os
import stat
import sys

from serverauditor_sshconfig.core.application import SSHConfigApplication, description
from serverauditor_sshconfig.core.api import API
from serverauditor_sshconfig.core.cryptor import RNCryptor
from serverauditor_sshconfig.core.logger import PrettyLogger
from serverauditor_sshconfig.core.ssh_config import SSHConfig


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

    def run(self):
        self._greeting()

        self._get_sa_user()
        self._get_sa_keys_and_connections()
        self._decrypt_sa_keys_and_connections()

        self._parse_local_config()
        self._sync_for_import()
        self._choose_new_hosts()
        self._create_keys_and_connections()

        self._valediction()
        return

    def _greeting(self):
        self._logger.log("ServerAuditor's ssh config script. Import from SA servers to local machine.", color='magenta')
        return

    @description("Synchronization...")
    def _sync_for_import(self):
        def get_identity_files(host):
            return [f[1] for f in host.get('identityfile', [])]

        # TODO: may be need to check local config hostname (also check conn['label'] and conn['hostname'])
        # TODO: true if host is found using label
        def is_exist(conn):
            attempt = conn['label'] or conn['hostname']
            h = self._config.get_host(attempt, substitute=True)
            key_check = True
            key_id = conn['ssh_key']
            if key_id:
                key_check = self._sa_keys[key_id['id']]['private_key'] in get_identity_files(h)
            return (conn['ssh_username'] == h['user'] and
                    conn['hostname'] == h['hostname'] and
                    conn['port'] == int(h.get('port', 22)) and
                    key_check)

        for conn in self._sa_connections[:]:
            if is_exist(conn):
                name = conn['label'] or "%s@%s:%s" % (conn['ssh_username'], conn['hostname'], conn['port'])
                self._logger.log('Connection "%s" can already be used by ssh.' % name, color='blue')
                self._sa_connections.remove(conn)

        return

    def _choose_new_hosts(self):
        def get_connection_name(conn, number):
            name = conn['label'] or "%s@%s:%s" % (conn['ssh_username'], conn['hostname'], conn['port'])
            return '%s (%d)' % (name, number)

        def get_connections_names():
            return [get_connection_name(c, i) for i, c in enumerate(self._sa_connections)]

        if not self._sa_connections:
            self._logger.log("There are no new connections on ServerAuditor's servers.")
            self._valediction()
            sys.exit(0)

        self._logger.log("The following new hosts have been founded on ServerAuditor's servers:", sleep=0)
        self._logger.log(get_connections_names())

        number = None
        while number != '=':
            number = raw_input("You may confirm this list (press '=') or remove host (enter number): ").strip()

            if number == '=':
                continue

            try:
                number = int(number)
                if number >= len(self._sa_connections) or number < 0:
                    raise IndexError
            except (ValueError, IndexError):
                self._logger.log("Incorrect index!", color='red', file=sys.stderr)
            else:
                self._sa_connections.pop(number)
                self._logger.log("Hosts:\n%s" % get_connections_names())

        self._logger.log("Ok!", color='green')
        return

    @description("Creating keys and connections...")
    def _create_keys_and_connections(self):
        def check_ssh_keys_dir():
            key_dir = os.path.expanduser(self.SSH_KEYS_DIR)
            if not os.path.exists(key_dir):
                os.mkdir(key_dir)

        def get_key_path(key):
            key_name = os.path.join(self.SSH_KEYS_DIR, key['label'])
            i = 1
            while os.path.exists(os.path.expanduser(key_name)):
                key_name += '-%d' % i
                i += 1
            return key_name

        def create_connection(conn):

            with open(self._config.USER_CONFIG_PATH, 'a') as cf:
                host = self.SSH_CONFIG_HOST_TEMPLATE.format(
                    host=conn['label'] or conn['hostname'],
                    hostname=conn['hostname'],
                    port=conn['port'],
                    user=conn['ssh_username']
                )
                cf.write(host)

                if conn['ssh_key']:
                    key = self._sa_keys[conn['ssh_key']['id']]
                    key_name = get_key_path(key)
                    idf = self.SSH_CONFIG_HOST_IDENTITY_FILE.format(key=key_name)
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
        pass
    return


if __name__ == "__main__":

    main()