# -*- coding: utf-8 -*-
"""Module with ssh sync provider."""
from os import environ
from os.path import expanduser
import re
from pathlib import Path
from paramiko.config import SSHConfig
from .base import BaseSyncService
from ...core.models.terminal import Host, SshConfig, SshIdentity, SshKey


class SSHService(BaseSyncService):
    """Synchronize ssh config content with application."""

    user_config = '~/.ssh/config'
    # pylint: disable=anomalous-backslash-in-string
    allowed_host_re = re.compile('[?*\[\]]')
    default_user = environ.get('USER', None)
    default_port = 22

    def __init__(self, *args, **kwargs):
        """Contruct new service to sync ssh config."""
        super(SSHService, self).__init__(*args, **kwargs)
        self.user_config = expanduser(self.user_config)

    def hosts(self):
        """Retrieve host instances from ssh config."""
        config = SSHConfig()
        with Path(self.user_config).open() as fileobj:
            config.parse(fileobj)
        hostnames = [i for i in config.get_hostnames() if self.is_endhost(i)]
        return [self.transform_to_instances(i, config.lookup(i))
                for i in hostnames]

    def transform_to_instances(self, alias, host):
        """Convert paramico host to application host."""
        return Host(
            label=alias,
            address=host['hostname'],
            ssh_config=SshConfig(
                port=host.get('port'),
                ssh_identity=SshIdentity(
                    username=host.get('user', self.default_user),
                    ssh_key=self.create_key(host)
                )
            ),
        )

    def is_endhost(self, hostname):
        """Return true when passed hostname is not wildcarded one."""
        return self.allowed_host_re.match(hostname) is None

    def create_key(self, config):
        """Construct new application ssh key instance."""
        if 'identityfile' not in config:
            return None
        identityfile = self.choose_ssh_key(config['identityfile'], config)
        if not identityfile:
            return None
        content = self._readkey(identityfile)
        return SshKey(label=identityfile.name, private_key=content)

    # pylint: disable=unused-argument,no-self-use
    def choose_ssh_key(self, sshkeys, host_config):
        """Choose single ssh key path instance from ones."""
        key_paths = [Path(i) for i in sshkeys]
        existed_paths = [i for i in key_paths if i.is_file()]
        return existed_paths and existed_paths[0]

    # pylint: disable=no-self-use
    def _readkey(self, sshkey_path):
        with sshkey_path.open('r') as _file:
            return _file.read()
