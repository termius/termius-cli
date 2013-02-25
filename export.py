#!/usr/bin/env python
#
# Copyright 2013 Crystalnix
#
# License will be here.

""" Short description.

Verbose description. Verbose description. Verbose description.
Verbose description. Verbose description. Verbose description.
Verbose description.

http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
http://stackoverflow.com/questions/1240275/how-to-negate-specific-word-in-regex
http://www.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3

TODO: Tests.
TODO: Exceptions.
TODO: Pythons 2.5-7, 3.0-3.
"""


from __future__ import print_function, with_statement

import base64
import getpass
import os
import pprint
import re
import socket
import sys
import urllib2

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print('Error! There is no any json library on your python!', file=sys.stderr)
        exit(1)


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

        Firstly, parser uses file which locates in USER_CONFIG_PATH.
        Then, file SYSTEM_CONFIG_PATH is used.
        """

        def is_file(path):
            """ Checks that file exists, and user have permissions for read it.

            :param path: path where file locates.
            :return: True or False.
            """
            return os.path.exists(path) and not os.path.isdir(path) and os.access(path, os.R_OK)

        for path in (self.USER_CONFIG_PATH, self.SYSTEM_CONFIG_PATH):
            if is_file(path):
                self._parse_file(path)
        return

    def _parse_file(self, path):
        """ Parses separated file.

        :raises Exception: if there is any unparsable line in file.
        :param path: path where file locates.
        """
        with open(path) as f:
            raw_settings = f.readlines()

        current_config = self._config[0]
        for line in raw_settings:
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

    def get_complete_host(self):
        """ Returns complete hosts.

        :return: list of hosts which names don't have masks.
        """

        def is_complete(host):
            """ Checks that host is complete.

            :param host: list of host's patterns.
            :return: True or False
            """
            return len(host) == 1 and '*' not in host and '?' not in host

        return [self.get_host(conf['host'][0]) for conf in self._config if is_complete(conf['host'])]

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

    def get_user_key(self):
        """ Asks username and password and then gets user's key token.

        Returns tuple (username, key).
        """
        username = raw_input('User: ')
        password = getpass.getpass()

        request = urllib2.Request(self.API_URL + "token/auth/")
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        try:
            result = urllib2.urlopen(request)
        except:
            print('What a shame!')
            return
        return username, json.load(result)['key']

    def create_keys_and_connections(self, settings, username, key):
        """ Creates keys and connections using settings.

        Sends request for creation keys and connections using username and key.
        """
        for k, v in settings.items():
            ssh_key = {
                'label': k,
                'passphrase': "what a pity!",
                'value': v['identityfile'],
                'type': 'private'
            }
            request = urllib2.Request(self.API_URL + "terminal/ssh_key/")
            request.add_header("Authorization", "ApiKey %s:%s" % (username, key))
            request.add_header("Content-Type", "application/json")
            try:
                result = urllib2.urlopen(request, json.dumps(ssh_key))
            except Exception, exc:
                print('What a shame!', exc)
                return

            print(result.info())

            key_number = int(result.headers['Location'].rstrip('/').rsplit('/', 1)[-1])

            connection = {
                "hostname": v['hostname'],
                "label": k,
                "ssh_key": key_number,
                "ssh_password": '',
                "ssh_username": v['user'],
                }

            request = urllib2.Request(self.API_URL + "terminal/connection/")
            request.add_header("Authorization", "ApiKey %s:%s" % (username, key))
            request.add_header("Content-Type", "application/json")
            try:
                result = urllib2.urlopen(request, json.dumps(connection))
            except Exception, exc:
                print('What a shame!', exc)
                return

            print(result.info())

            print ('*' * 100)


VERBOSE = True


def log(message, *args, **kwargs):
    """ If VERBOSE = True, prints message. """
    if VERBOSE:
        print(message, *args, **kwargs)
    return

if __name__ == "__main__":

    pass