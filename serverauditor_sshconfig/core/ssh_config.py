# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import getpass
import os
import re
import socket


class SSHConfigException(Exception):
    pass


class SSHConfig(object):
    """ Representation of ssh config information.

    For information about the format see OpenSSH's man page.
    Based on paramiko.config.SSHConfig.
    """

    USER_CONFIG_PATH = os.path.expanduser('~/.ssh/config')
    SYSTEM_CONFIG_PATH = '/etc/ssh/ssh_config'
    SSH_PORT = '22'

    def __init__(self):
        self._config = [{'host': ['*']}]

    def _is_file_ok(self, path):
        """ Checks that file exists, and user have permissions for read it.

        :param path: path where file is located.
        :return: True or False.
        """

        return os.path.exists(path) and not os.path.isdir(path) and os.access(path, os.R_OK)

    def parse(self):
        """ Parses configuration files.

        Firstly, parser uses file which is located in USER_CONFIG_PATH.
        Then, file SYSTEM_CONFIG_PATH is used.
        """

        def create_config_file():
            """ Creates configuration file. """
            ssh_dir = os.path.dirname(path)
            if not os.path.exists(ssh_dir):
                os.mkdir(ssh_dir, 0o700)

            with open(path, 'w') as f:
                f.write("# File was created by ServerAuditor\n\n")

            return

        for path in (self.USER_CONFIG_PATH, ):  # self.SYSTEM_CONFIG_PATH):
            if not self._is_file_ok(path):
                create_config_file()
            else:
                with open(path) as f:
                    self._parse_file(f)

        return

    def _parse_file(self, file_object):
        """ Parses separated file.

        :raises SSHConfigException: if there is any unparsable line in file.
        :param file_object: file.
        """

        settings_regex = re.compile(r'(\w+)(?:\s*=\s*|\s+)(.+)')
        current_config = self._config[0]
        for line in file_object:
            line = line.strip()
            if (line == '') or (line[0] == '#'):
                continue

            match = re.match(settings_regex, line)
            if not match:
                raise SSHConfigException("Unparsable line %s" % line)
            key = match.group(1).lower()
            value = match.group(2)

            if key == 'host':
                current_config = {}
                if value.startswith('"') and value.endswith('"'):
                    current_config['host'] = [value[1:-1]]
                else:
                    current_config['host'] = value.split()
                self._config.append(current_config)
            else:
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                if key in ['identityfile', 'localforward', 'remoteforward']:
                    current_config.setdefault(key, []).append(value)
                elif key not in current_config:
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
            is_key = True  # 'identityfile' in conf
            return is_full_name and is_key

        return [conf['host'][0] for conf in self._config if is_complete(conf)]

    def get_host(self, host, substitute=False):
        """ Returns config for host.

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
                name = pattern.lstrip('!').replace('.', '\.').replace('*', '.+').replace('?', '.')
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
                    if isinstance(v, list):
                        settings[k] = v[:]
                    else:
                        settings[k] = v

        if substitute:
            self._substitute_variables(settings)
        return settings

    def _substitute_variables(self, settings):
        """ Substitutes variables in settings.

        :raises SSHConfigException: if user does not permissions for read IdentityFile.
        :param settings: config which will be changed.
        """

        if 'hostname' in settings:
            settings['hostname'] = settings['hostname'].replace('%h', settings['host'])
        else:
            settings['hostname'] = settings['host']

        if 'port' in settings:
            port = settings['port']
        else:
            port = self.SSH_PORT

        settings['port'] = int(port)

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
                    if isinstance(settings[k], list):
                        for i in range(len(settings[k])):
                            settings[k][i] = settings[k][i].replace(find, replace)
                    else:
                        settings[k] = settings[k].replace(find, replace)

        if 'identityfile' in settings:
            for i, name in enumerate(settings['identityfile']):
                if self._is_file_ok(name):
                    name = name[name.rfind('/') + 1:]
                    with open(settings['identityfile'][i]) as f:
                        settings['identityfile'][i] = [name, f.read()]
            #else:
            #    raise SSHConfigException('Can not read IdentityFile %s' % settings['identityfile'])

        return
