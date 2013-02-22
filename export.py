#!/usr/bin/env python
#
# Copyright 2013 Crystalnix
#
# License will be here.

""" Short description.

Verbose description. Verbose description. Verbose description.
Verbose description. Verbose description. Verbose description.
Verbose description.
"""


from __future__ import print_function, with_statement

import base64
import fnmatch
import getpass
import os
import pprint
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


#  paramiko.config.SSHConfig
import re
import socket

SSH_PORT = 22
proxy_re = re.compile(r"^(proxycommand)\s*=*\s*(.*)", re.I)


class SSHConfig (object):
    """
Representation of config information as stored in the format used by
OpenSSH. Queries can be made via L{lookup}. The format is described in
OpenSSH's C{ssh_config} man page. This class is provided primarily as a
convenience to posix users (since the OpenSSH format is a de-facto
standard on posix) but should work fine on Windows too.

@since: 1.6
"""

    def __init__(self):
        """
Create a new OpenSSH config object.
"""
        self._config = [ { 'host': '*' } ]

    def parse(self, file_obj):
        """
Read an OpenSSH config from the given file object.

@param file_obj: a file-like object to read the config file from
@type file_obj: file
"""
        configs = [self._config[0]]
        for line in file_obj:
            line = line.rstrip('\n').lstrip()
            if (line == '') or (line[0] == '#'):
                continue
            if '=' in line:
                # Ensure ProxyCommand gets properly split
                if line.lower().strip().startswith('proxycommand'):
                    match = proxy_re.match(line)
                    key, value = match.group(1).lower(), match.group(2)
                else:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
            else:
                # find first whitespace, and split there
                i = 0
                while (i < len(line)) and not line[i].isspace():
                    i += 1
                if i == len(line):
                    raise Exception('Unparsable line: %r' % line)
                key = line[:i].lower()
                value = line[i:].lstrip()

            if key == 'host':
                del configs[:]
                # the value may be multiple hosts, space-delimited
                for host in value.split():
                    # do we have a pre-existing host config to append to?
                    matches = [c for c in self._config if c['host'] == host]
                    if len(matches) > 0:
                        configs.append(matches[0])
                    else:
                        config = { 'host': host }
                        self._config.append(config)
                        configs.append(config)
            else:
                for config in configs:
                    config[key] = value

    def lookup(self, hostname):
        """
Return a dict of config options for a given hostname.

The host-matching rules of OpenSSH's C{ssh_config} man page are used,
which means that all configuration options from matching host
specifications are merged, with more specific hostmasks taking
precedence. In other words, if C{"Port"} is set under C{"Host *"}
and also C{"Host *.example.com"}, and the lookup is for
C{"ssh.example.com"}, then the port entry for C{"Host *.example.com"}
will win out.

The keys in the returned dict are all normalized to lowercase (look for
C{"port"}, not C{"Port"}. No other processing is done to the keys or
values.

@param hostname: the hostname to lookup
@type hostname: str
"""
        matches = [x for x in self._config if fnmatch.fnmatch(hostname, x['host'])]
        # Move * to the end
        _star = matches.pop(0)
        matches.append(_star)
        ret = {}
        for m in matches:
            for k,v in m.iteritems():
                if not k in ret:
                    ret[k] = v
        ret = self._expand_variables(ret, hostname)
        del ret['host']
        return ret

    def _expand_variables(self, config, hostname ):
        """
Return a dict of config options with expanded substitutions
for a given hostname.

Please refer to man ssh_config(5) for the parameters that
are replaced.

@param config: the config for the hostname
@type hostname: dict
@param hostname: the hostname that the config belongs to
@type hostname: str
"""

        if 'hostname' in config:
            config['hostname'] = config['hostname'].replace('%h',hostname)
        else:
            config['hostname'] = hostname

        if 'port' in config:
            port = config['port']
        else:
            port = SSH_PORT

        user = os.getenv('USER')
        if 'user' in config:
            remoteuser = config['user']
        else:
            remoteuser = user

        host = socket.gethostname().split('.')[0]
        fqdn = socket.getfqdn()
        homedir = os.path.expanduser('~')
        replacements = {
            'controlpath': [
                ('%h', config['hostname']),
                ('%l', fqdn),
                ('%L', host),
                ('%n', hostname),
                ('%p', port),
                ('%r', remoteuser),
                ('%u', user)
            ],
            'identityfile': [
                ('~', homedir),
                ('%d', homedir),
                ('%h', config['hostname']),
                ('%l', fqdn),
                ('%u', user),
                ('%r', remoteuser)
            ],
            'proxycommand': [
                ('%h', config['hostname']),
                ('%p', port),
                ('%r', remoteuser),
                ],
            }
        for k in config:
            if k in replacements:
                for find, replace in replacements[k]:
                    config[k] = config[k].replace(find, str(replace))
        return config

VERBOSE = True
API_URL = 'http://dev.serverauditor.com/api/v1/'
USER_CONFIG_PATH = os.path.expanduser('~/.ssh/config')
SYSTEM_CONFIG_PATH = '/etc/ssh/ssh_config'
CONFIG_PATH_ORDER = [USER_CONFIG_PATH, SYSTEM_CONFIG_PATH]


def log(message, *args, **kwargs):
    """ If VERBOSE = True, prints message. """
    if VERBOSE:
        print(message, *args, **kwargs)
    return


def check_file(path):
    """ Checks existence and permissions of file.

    :param path: path to file
    :type path: str
    """
    return os.path.exists(path) and os.path.isfile(path) and os.access(path, os.R_OK)


def get_setting(path):
    """ Gets setting from file and processes them.

    :param path: path to file
    :type path: str
    """

    if check_file(path):
        config = SSHConfig()

        with open(path) as f:
            config.parse(f)

        hosts_array = config._config
        hosts = {}
        for host in hosts_array:
            name = host['host']
            if '*' not in name:
                hosts[name] = config.lookup(name)

        if process_settings(hosts):
            return hosts, True

    return False, False


def process_settings(settings):
    """ Processes settings.

    Gets identityFile's content if exists. Adds hostname if does not exist.
    Returns False if there is error else True.
    """
    for label, value in settings.items():
        if 'identityfile' in value:
            path = os.path.expanduser(value['identityfile'])
            if check_file(path):
                with open(path) as f:
                    value['identityfile'] = f.read()
            # else:
            #     return False
        if 'hostname' not in value:
            value['hostname'] = label

    return True


def read_files():
    """ Reads settings from files.

    Tries to get setting from files '~/.ssh/config', '/etc/ssh/ssh_config' and
    file which user will set, in order.
    Returns the value of the first existing one. If none exists, script will exit.
    """

    settings = False
    read = False
    for path in CONFIG_PATH_ORDER:
        settings, read = get_setting(path)
        if read:
            break

    if not read:
        path = raw_input('Directory:\n')
        settings, read2 = get_setting(os.path.expanduser(path))

        if not read2:
            print('Error! There is no any valid ssh config on your computer!', file=sys.stderr)
            exit(1)

    pprint.pprint(settings)

    return settings


def get_user_key():
    """ Asks username and password and then gets user's key token.

    Returns tuple (username, key).
    """
    username = raw_input('User: ')
    password = getpass.getpass()

    request = urllib2.Request(API_URL + "token/auth/")
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    try:
        result = urllib2.urlopen(request)
    except:
        print('What a shame!')
        return
    return username, json.load(result)['key']


def crypt(username, key):
    pass


def create_keys_and_connections(settings, username, key):
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
        request = urllib2.Request(API_URL + "terminal/ssh_key/")
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

        request = urllib2.Request(API_URL + "terminal/connection/")
        request.add_header("Authorization", "ApiKey %s:%s" % (username, key))
        request.add_header("Content-Type", "application/json")
        try:
            result = urllib2.urlopen(request, json.dumps(connection))
        except Exception, exc:
            print('What a shame!', exc)
            return

        print(result.info())

        print ('*' * 100)


def main():
    settings = read_files()
    username, key = get_user_key()
    crypt(username, key)
    create_keys_and_connections(settings, username, key)
    return


if __name__ == "__main__":

    main()

