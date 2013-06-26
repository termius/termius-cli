#!/usr/bin/env python
#
# Copyright 2013 Crystalnix

import sys

from core.application import SSHConfigApplication, description
from core.api import API
from core.cryptor import RNCryptor
from core.logger import PrettyLogger
from core.ssh_config import SSHConfig


class ImportSSHConfigApplication(SSHConfigApplication):

    SSH_CONFIG_HOST_TEMPLATE = """\
# created by ServerAuditor
Host {host}
    User {user}
    HostName {hostname}
    Port {port}\n
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
        def is_exist(conn):
            for attempt in (conn['hostname'], conn['label']):
                h = self._config.get_host(attempt, substitute=True)
                key_id = conn['ssh_key']
                if (conn['ssh_username'] == h['user'] and
                        conn['port'] == int(h.get('port', 22))):
                        # key check
                    return True
            # TODO: may be need to check local config's hostnames
            return False

        for conn in self._sa_connections[:]:
            if is_exist(conn):
                self._sa_connections.remove(conn)

        return

    def _choose_new_hosts(self):
        def get_connection_name(conn, number):
            name = conn['label'] or "%s@%s:%s" % (conn['ssh_username'], conn['hostname'], conn['port'])
            return '%s (%d)' % (name, number)

        self._logger.log("The following new hosts have been founded on ServerAuditor's servers:", sleep=0)
        self._logger.log([get_connection_name(c, i) for i, c in enumerate(self._sa_connections)])

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
                self._logger.log("Bad index!", color='red', file=sys.stderr)
            else:
                self._sa_connections.pop(number)
                self._logger.log("Hosts:\n%s" % [get_connection_name(c, i) for i, c in enumerate(self._sa_connections)])

        self._logger.log("Ok!", color='green')
        return

    @description("Creating keys and connections...")
    def _create_keys_and_connections(self):
        def create_connection(conn):
            with open(self._config.USER_CONFIG_PATH, 'a') as cf:
                host = self.SSH_CONFIG_HOST_TEMPLATE.format(
                    host=conn['label'] or conn['hostname'],
                    hostname=conn['hostname'],
                    port=conn['port'],
                    user=conn['ssh_username']
                )
                cf.write(host)

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