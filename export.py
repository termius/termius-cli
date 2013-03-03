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
http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
http://www.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3

TODO: Create tests.
TODO: Create and handle exceptions.
TODO: Check on python 2.5-7, 3.0-4. (see tox)
TODO: Check existing keys and connection.
TODO: Add crypto.
TODO: ...
"""


from __future__ import print_function, with_statement

import base64
import getpass
import os
import pprint
import re
import socket
import sys
import time
import urllib2

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print('There is no any json library installed on your python!', file=sys.stderr)
        sys.exit(1)


class SSHConfig(object):
    """ Representation of ssh config information.

    For information about the format see OpenSSH's man page.
    Based on paramiko.config.SSHConfig.
    """

    USER_CONFIG_PATH = os.path.expanduser('~/.ssh/config')
    SYSTEM_CONFIG_PATH = '/etc/ssh/ssh_config'
    SETTINGS_REGEX = re.compile(r'(\w+)(\s*=\s*|\s+)(.+)')
    SSH_PORT = '22'

    def __init__(self):
        self._config = [{'host': ['*']}]

    def parse(self):
        """ Parses configuration files.

        Firstly, parser uses file which is located in USER_CONFIG_PATH.
        Then, file SYSTEM_CONFIG_PATH is used.
        """

        def is_file(path):
            """ Checks that file exists, and user have permissions for read it.

            :param path: path where file is located.
            :return: True or False.
            """
            return os.path.exists(path) and not os.path.isdir(path) and os.access(path, os.R_OK)

        is_parsed = False

        for path in (self.USER_CONFIG_PATH, ):#self.SYSTEM_CONFIG_PATH):
            if is_file(path):
                is_parsed = True
                with open(path) as f:
                    self._parse_file(f)

        return is_parsed

    def _parse_file(self, file_object):
        """ Parses separated file.

        :raises Exception: if there is any unparsable line in file.
        :param file_object: file.
        """

        current_config = self._config[0]
        for line in file_object:
            line = line.strip()
            if (line == '') or (line[0] == '#'):
                continue

            match = re.match(self.SETTINGS_REGEX, line)
            if not match:
                raise Exception("Unparsable line %s" % line)
            key = match.group(1).lower()
            value = match.group(3)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            if key == 'host':
                self._config.append({})
                current_config = self._config[-1]
                current_config['host'] = value.split()
            else:
                current_config[key] = value

        return

    def get_complete_hosts(self):
        """ Returns complete hosts.

        :return: list of hosts which names don't have masks.
        """

        def is_complete(conf):
            """ Checks that host is complete.

            :param conf: config.
            :return: True or False
            """
            host = conf['host']
            is_full_name = len(host) == 1 and '*' not in host and '?' not in host
            is_key = 'identityfile' in conf
            return is_full_name and is_key

        return [conf['host'][0] for conf in self._config if is_complete(conf)]

    def get_host(self, host, substitute=False):
        """ Returns config fot host.

        :param host: host's name
        :param substitute: if True all patterns will be substituted.
        :return: config for host.
        """

        def is_match(patterns):
            """ Checks that host applies patterns.

            :param patterns: list of patterns.
            :return: True or False
            """
            positive = []
            negative = []
            for pattern in patterns:
                is_negative = pattern.startswith('!')
                name = pattern.lstrip('!').replace('*', '.+').replace('?', '.')
                name += '$'
                match = re.match(name, host)
                if is_negative:
                    negative.append(match)
                else:
                    positive.append(match)

            return any(positive) and not any(negative)

        matches = [h for h in self._config if is_match(h['host'])]
        settings = {'host': host}
        for m in matches:
            for k, v in m.items():
                if k not in settings:
                    settings[k] = v

        if substitute:
            return self._substitute_variables(settings)
        return settings

    def _substitute_variables(self, settings):
        """ Substituted variables in settings.

        :raises Exception: if user does not permissions for read IdentityFile.
        :param settings: config which will be changed.
        :return: settings
        """

        def is_file(path):
            return os.path.exists(path) and not os.path.isdir(path) and os.access(path, os.R_OK)

        if 'hostname' in settings:
            settings['hostname'] = settings['hostname'].replace('%h', settings['host'])
        else:
            settings['hostname'] = settings['host']

        if 'port' in settings:
            port = settings['port']
        else:
            port = self.SSH_PORT

        user = getpass.getuser()
        if 'user' not in settings:
            settings['user'] = user

        home_dir = os.path.expanduser('~')

        host = socket.gethostname().split('.')[0]
        fqdn = socket.getfqdn()

        replacements = {
            'controlpath': [
                ('%h', settings['hostname']),
                ('%l', fqdn),
                ('%L', host),
                ('%n', settings['host']),
                ('%p', port),
                ('%r', settings['user']),
                ('%u', user)
            ],
            'loaclcommand': [
                ('%d', home_dir),
                ('%h', settings['hostname']),
                ('%l', fqdn),
                ('%n', settings['host']),
                ('%p', port),
                ('%r', settings['user']),
                ('%u', user)
            ],
            'identityfile': [
                ('~', home_dir),
                ('%d', home_dir),
                ('%h', settings['hostname']),
                ('%l', fqdn),
                ('%u', user),
                ('%r', settings['user'])
            ],
            'proxycommand': [
                ('%h', settings['hostname']),
                ('%p', port),
            ],
        }

        for k in settings:
            if k in replacements:
                for find, replace in replacements[k]:
                    settings[k] = settings[k].replace(find, replace)

        if 'identityfile' in settings:
            if is_file(settings['identityfile']):
                with open(settings['identityfile']) as f:
                    settings['identityfile'] = f.read()
            #else:
            #    raise Exception('Can not read IdentityFile %s' % settings['identityfile'])

        return settings


class API(object):

    API_URL = 'http://dev.serverauditor.com/api/v1/'

    def get_key(self, username, password):
        """ Returns user's key token. """

        request = urllib2.Request(self.API_URL + "token/auth/")
        auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % auth)
        result = urllib2.urlopen(request)

        return json.load(result)['key']

    def get_keys_and_connections(self, username, key):
        """ Gets current keys and connections.

        Sends request for getting keys and connections using username and key.
        """
        request = urllib2.Request(self.API_URL + "terminal/ssh_key/?limit=100")
        request.add_header("Authorization", "ApiKey %s:%s" % (username, key))
        request.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(request)
        keys = json.loads(response.read())['objects']

        request = urllib2.Request(self.API_URL + "terminal/connection/?limit=100")
        request.add_header("Authorization", "ApiKey %s:%s" % (username, key))
        request.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(request)
        connections = json.loads(response.read())['objects']

        return keys, connections

    def create_keys_and_connections(self, hosts, username, key):
        """ Creates keys and connections using hosts' configs.

        Sends request for creation keys and connections using username and key.
        """
        for host in hosts:
            ssh_key = {
                'label': host['host'],
                'passphrase': ".",
                'value': host['identityfile'],
                'type': 'private'
            }
            request = urllib2.Request(self.API_URL + "terminal/ssh_key/")
            request.add_header("Authorization", "ApiKey %s:%s" % (username, key))
            request.add_header("Content-Type", "application/json")
            response = urllib2.urlopen(request, json.dumps(ssh_key))

            key_number = int(response.headers['Location'].rstrip('/').rsplit('/', 1)[-1])
            connection = {
                "hostname": host['hostname'],
                "label": host['host'],
                "ssh_key": key_number,
                "ssh_password": '',
                "ssh_username": host['user'],
            }
            request = urllib2.Request(self.API_URL + "terminal/connection/")
            request.add_header("Authorization", "ApiKey %s:%s" % (username, key))
            request.add_header("Content-Type", "application/json")
            response = urllib2.urlopen(request, json.dumps(connection))

        return


class Application(object):

    VERBOSE = True

    def __init__(self):
        self._config = SSHConfig()
        self._api = API()
        self._hosts = None
        self._full_hosts = None
        self._sa_username = None
        self._sa_key = None
        self._sa_keys = None
        self._sa_connections = None

    def run(self):
        self._get_sa_user()
        self._get_keys_and_connections()
        self._parse_config()
        self._sync()
        self._get_hosts()
        self._get_full_hosts()
        self._create_keys_and_connections()
        return

    def _log(self, message, is_pprint=False, sleep=0.5, color=None, *args, **kwargs):
        if self.VERBOSE:
            if is_pprint:
                pprint.pprint(message, *args, **kwargs)
            else:
                print(message, *args, **kwargs)
            if sleep:
                time.sleep(sleep)
        return

    def _parse_config(self):
        self._log("Parsing...")
        is_parsed = self._config.parse()
        if not is_parsed:
            self._log("There is no local ssh config on your computer! "
                      "This file must be located in '%s'!" % self._config.USER_CONFIG_PATH, file=sys.stderr)
            sys.exit(1)
        self._hosts = self._config.get_complete_hosts()
        self._log("Success!")
        return

    def _sync(self):
        self._log("Synchronization...")

        def is_exist(host):
            h = self._config.get_host(host, substitute=True)
            for conn in self._sa_connections:
                key_id = conn['ssh_key']
                if key_id and \
                        conn['hostname'] == h['hostname'] and \
                        conn['label'] == h['host'] and \
                        conn['ssh_username'] == h['user'] and \
                        self._sa_keys[key_id['id']]['value'] == h['identityfile']:
                    return True
            return False

        hosts = self._hosts[:]
        for host in hosts:
            if is_exist(host):
                self._hosts.remove(host)
        self._log("Success!")
        return

    def _get_hosts(self):
        self._log("The following new hosts have been founded in your ssh config:")
        self._log(self._hosts)
        number = None
        while number != '0':
            number = raw_input("You may confirm this list (press '0'), "
                               "add new host (press '1') or "
                               "remove host (press '2'): ").strip()
            if number == '1':
                host = raw_input("Adding host: ")
                conf = self._config.get_host(host)
                if conf.keys() == ['host']:
                    self._log("There is no config for host %s!" % host, file=sys.stderr)
                else:
                    self._hosts.append(host)

                self._log("Hosts:\n%s" % self._hosts)

            elif number == '2':
                host = raw_input("Deleting host: ")
                if host in self._hosts:
                    self._hosts.remove(host)
                else:
                    self._log("There is no host %s!" % host, file=sys.stderr)

                self._log("Hosts:\n%s" % self._hosts)

        self._log("Ok!")

        return

    def _get_full_hosts(self):
        self._full_hosts = [self._config.get_host(h, substitute=True) for h in self._hosts]
        return

    def _get_sa_user(self):
        self._sa_username = raw_input("Enter your Server Auditor's username: ").strip()
        password = getpass.getpass("Enter your Server Auditor's password: ")
        try:
            self._sa_key = self._api.get_key(self._sa_username, password)
        except Exception as exc:
            self._log("Error! %s" % exc, file=sys.stderr)
            sys.exit(1)

        self._log("Success!")
        return

    def _get_keys_and_connections(self):
        self._log("Getting current keys and connections...")
        try:
            keys, self._sa_connections = self._api.get_keys_and_connections(self._sa_username, self._sa_key)
        except Exception as exc:
            self._log("Error! %s" % exc, file=sys.stderr)
            sys.exit(1)

        self._sa_keys = {}
        for key in keys:
            self._sa_keys[key['id']] = key
        self._log("Success!")

        return

    def _create_keys_and_connections(self):
        self._log("Creating keys and connections...")
        try:
            self._api.create_keys_and_connections(self._full_hosts, self._sa_username, self._sa_key)
        except Exception as exc:
            self._log("Error! %s" % exc, file=sys.stderr)
        else:
            self._log("Success!")

        return


def main():
    app = Application()
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    print("Bye!")
    return


if __name__ == "__main__":

    main()