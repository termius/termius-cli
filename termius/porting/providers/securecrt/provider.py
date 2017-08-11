# -*- coding: utf-8 -*-
"""Module with SecureCRT provider."""
import logging
import xml

from termius.core.models.terminal import Host, SshConfig, Identity, SshKey, \
    Group
from termius.porting.providers.securecrt.parser import SecureCRTConfigParser

from ..base import BasePortingProvider


class SecureCRTPortingProvider(BasePortingProvider):
    """Synchronize secure crt config content with application."""

    logger = logging.getLogger(__name__)

    def __init__(self, source, *args, **kwargs):
        """Contruct new service to sync ssh config."""
        super(SecureCRTPortingProvider, self).__init__(*args, **kwargs)

        self.config_source = source

    def export_hosts(self):
        """Skip export."""
        pass

    def provider_hosts(self):
        """Retrieve host instances from ssh config."""
        root = xml.etree.ElementTree.parse(self.config_source).getroot()
        hosts = []

        raw_hosts = SecureCRTConfigParser.parse_hosts(
            root
        )
        identity_paths = SecureCRTConfigParser.parse_identity(root)
        main_group = Group(label='SecureCRT')

        group_config = SshConfig(
            identity=Identity(
                is_visible=False,
                label='SecureCRT'
            )
        )

        if identity_paths:
            try:
                with open(identity_paths[0], 'rb') as private_key_file:
                    private_key = private_key_file.read()

                with open(identity_paths[1], 'rb') as public_key_file:
                    public_key = public_key_file.read()

                key = SshKey(
                    label='SecureCRT',
                    private_key=private_key,
                    public_key=public_key
                )
                group_config.identity.ssh_key = key
            except IOError:
                self.logger.info(
                    'Cannot find SSH2 raw key %s' % identity_paths[1]
                )

        main_group.ssh_config = group_config

        for raw_host in raw_hosts:
            host = Host(
                label=raw_host['label'],
                address=raw_host['hostname']
            )
            host.group = main_group
            ssh_config = SshConfig(
                port=raw_host['port'],
                identity=Identity(
                    username=raw_host.get('username'),
                    is_visible=False,
                    label=raw_host.get('username')
                )
            )

            host.ssh_config = ssh_config

            hosts.append(host)

        return hosts
