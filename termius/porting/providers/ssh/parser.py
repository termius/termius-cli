# -*- coding: utf-8 -*-
"""Module with ssh config parser."""

import re
from paramiko.config import SSHConfig


class SSHConfigParser(SSHConfig):
    """Class to override parse method of paramiko parser."""

    def parse(self, file_obj): # noqa
        """
        Read an OpenSSH config from the given file object.

        :param file_obj: a file-like object to read the config file from
        """
        termius_ignore_regexp = re.compile(r'# termius:ignore')

        host = {'host': ['*'], 'config': {}}

        for line in file_obj:
            line = line.strip()

            if not line:
                continue

            if line.startswith('#'):
                ignore_comment = termius_ignore_regexp.match(line)

                if ignore_comment:
                    host['config']['ignore'] = ''

                continue

            match = re.match(self.SETTINGS_REGEX, line)
            if not match:
                raise Exception('Unparsable line %s' % line)
            key = match.group(1).lower()
            value = match.group(2)
            if key == 'host':
                self._config.append(host)
                host = {
                    'host': self._get_hosts(value),
                    'config': {}
                }

            elif key == 'proxycommand' and value.lower() == 'none':
                host['config'][key] = None
            else:
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                if key in ['identityfile', 'localforward', 'remoteforward']:
                    if key in host['config']:
                        host['config'][key].append(value)
                    else:
                        host['config'][key] = [value]
                elif key not in host['config']:
                    host['config'][key] = value

        self._config.append(host)
