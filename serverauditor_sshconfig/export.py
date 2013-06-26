#!/usr/bin/env python
#
# Copyright 2013 Crystalnix

import sys

from core.application import SSHConfigApplication
from core.api import API
from core.cryptor import RNCryptor
from core.logger import PrettyLogger
from core.ssh_config import SSHConfig


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
        self._logger.log("ServerAuditor's ssh config script. Export from local machine to SA servers.", color='magenta')
        return

    def _sync_for_export(self):
        def is_exist(host):
            h = self._config.get_host(host, substitute=True)
            for conn in self._sa_connections:
                key_id = conn['ssh_key']
                if (conn['hostname'] == h['hostname'] and
                        conn['ssh_username'] == h['user'] and
                        conn['port'] == int(h.get('port', 22))):
                        # conn['label'] == h['host'] and
                        # self._sa_keys[key_id['id']]['value'] in h['identityfile']
                    return True
            return False

        self._logger.log("Synchronization...")

        for host in self._local_hosts[:]:
            if is_exist(host):
                self._local_hosts.remove(host)

        self._logger.log("Success!", color='green')
        return

    def _choose_new_hosts(self):
        self._logger.log("The following new hosts have been founded in your ssh config:", sleep=0)
        self._logger.log(self._local_hosts)
        number = None
        while number != '=':
            number = raw_input("You may confirm this list (press '='), "
                               "add (press '+') or remove (press '-') host: ").strip()
            if number == '+':
                host = raw_input("Adding host: ")
                conf = self._config.get_host(host)
                if conf.keys() == ['host']:
                    self._logger.log("There is no config for host %s!" % host, file=sys.stderr)
                else:
                    self._local_hosts.append(host)

                self._logger.log("Hosts:\n%s" % self._local_hosts)

            elif number == '-':
                host = raw_input("Deleting host: ")
                if host in self._local_hosts:
                    self._local_hosts.remove(host)
                else:
                    self._logger.log("There is no host %s!" % host, file=sys.stderr)

                self._logger.log("Hosts:\n%s" % self._local_hosts)

        self._logger.log("Ok!", color='green')
        return

    def _get_full_hosts(self):
        def encrypt_host(host):
            host['host'] = self._cryptor.encrypt(host['host'], self._sa_master_password)
            host['hostname'] = self._cryptor.encrypt(host['hostname'], self._sa_master_password)
            host['user'] = self._cryptor.encrypt(host['user'], self._sa_master_password)
            host['password'] = self._cryptor.encrypt('', self._sa_master_password)
            return host

        self._logger.log("Getting full information...")
        self._full_local_hosts = [encrypt_host(self._config.get_host(h, substitute=True)) for h in self._local_hosts]

        self._logger.log("Success!", color='green')
        return

    def _create_keys_and_connections(self):
        self._logger.log("Creating keys and connections...")
        try:
            self._api.create_keys_and_connections(self._full_local_hosts, self._sa_username, self._sa_auth_key)
        except Exception as exc:
            self._logger.log("Error! %s" % exc, file=sys.stderr)
            sys.exit(1)

        self._logger.log("Success!", color='green')
        return


def main():
    app = ExportSSHConfigApplication(api=API(), ssh_config=SSHConfig(), cryptor=RNCryptor(), logger=PrettyLogger())
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        pass
    return


if __name__ == "__main__":

    main()