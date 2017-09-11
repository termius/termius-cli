# -*- coding: utf-8 -*-
"""Module with ssh sync provider."""
import re

from os.path import expanduser
from pathlib2 import Path

from termius.core.models.terminal import Host

from ..base import BasePortingProvider
from .parser import SSHConfigParser
from .adapter import SSHConfigHostAdapter


class SSHPortingProvider(BasePortingProvider):
    """Synchronize ssh config content with application."""

    user_config = '~/.ssh/config'
    export_path = expanduser('~/.termius/sshconfig')

    # pylint: disable=anomalous-backslash-in-string
    allowed_host_re = re.compile('[?*\[\]]')
    default_port = 22

    def __init__(self, *args, **kwargs):
        """Contruct new service to sync ssh config."""
        super(SSHPortingProvider, self).__init__(*args, **kwargs)
        self.user_config = expanduser(self.user_config)
        self.adapter = SSHConfigHostAdapter()

    def export_hosts(self):
        """Export app hosts to ssh config syntax."""
        hosts_in_storage = self.storage.get_all(Host)
        with Path(self.export_path).open(mode='w+') as export_file:
            for host in hosts_in_storage:
                self.export_host(
                    export_file,
                    host.get('label', host['address']),
                    self.adapter.adapt_instance_to_ssh_config_host(host)
                )

    def provider_hosts(self):
        """Retrieve host instances from ssh config."""
        parser = SSHConfigParser()
        with Path(self.user_config).open() as config:
            parser.parse(config)

        parsed_hosts = [
            i for i in parser.get_hostnames() if self.is_endhost(i)
        ]

        to_import = []

        for alias in parsed_hosts:
            parsed_host = parser.lookup(alias)

            if 'ignore' in parsed_host:
                continue

            to_import.append(
                self.adapter.adapt_ssh_config_host_to_instance(
                    alias, parsed_host
                )
            )

        return to_import

    def is_endhost(self, hostname):
        """Return true when passed hostname is not wildcarded one."""
        return self.allowed_host_re.match(hostname) is None

    def export_host(self, export_file, alias, attributes):
        """Write host to target file."""
        def make_param(param, value):
            return '\n    %s %s' % (param, value)

        host_string = '\nHost %s' % alias

        for key, value in attributes.iteritems():
            host_string += make_param(key, value)

        export_file.write(host_string + '\n')
