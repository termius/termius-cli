# -*- coding: utf-8 -*-
"""Module with SecureCRT provider."""
import logging
from xml.etree import ElementTree

from termius.core.models.terminal import Host, SshConfig, Identity, SshKey, \
    Group
from termius.porting.providers.securecrt.parser import SecureCRTConfigParser

from ..base import BasePortingProvider


class SecureCRTPortingProvider(BasePortingProvider):
    """Synchronize secure crt config content with application."""

    logger = logging.getLogger(__name__)

    def __init__(self, source, *args, **kwargs):
        """Construct provider instance."""
        super(SecureCRTPortingProvider, self).__init__(*args, **kwargs)

        xml_root = ElementTree.parse(source).getroot()
        self.parser = SecureCRTConfigParser(xml_root)

    def export_hosts(self):
        """Skip export."""
        pass

    def provider_hosts(self):
        """Retrieve SecureCRT sessions from xml config."""
        result_hosts = []
        tree = self.parser.parse_hosts()

        root_group = Group(label='SecureCRT')

        identity_paths = self.parser.parse_identity()
        if identity_paths:
            self.logger.info('Found private key path: %s' % identity_paths[0])
            self.logger.info('Found public key path: %s' % identity_paths[1])
            try:
                key = self.create_key(identity_paths)
                root_group.ssh_config = SshConfig(
                    identity=Identity(
                        ssh_key=key,
                        label='SecureCRT',
                        is_visible=False
                    )
                )
            except IOError:
                self.logger.info(
                    'Warning: cannot import SSH2 raw key %s' %
                    identity_paths[1]
                )

        self.create_entries_from_tree(tree, result_hosts, root_group)
        self.logger.info('Parsed hosts %i' % len(result_hosts))
        self.logger.info('Importing...')
        return result_hosts

    def create_entries_from_tree(self, tree, result_hosts, parent_group=None):
        """Create instances from groups tree."""
        for label, node in tree.items():
            if not isinstance(node, dict):
                continue

            if not node.get('__group', None):
                result_hosts.append(
                    self.create_host(node, parent_group)
                )
            else:
                group = Group(label=label, parent_group=parent_group)
                self.create_entries_from_tree(node, result_hosts, group)

    def create_host(self, raw_host, group):
        """Create instances from groups tree."""
        host = Host(
            label=raw_host['label'],
            address=raw_host['hostname'],
            group=group
        )
        host.ssh_config = SshConfig(
            port=raw_host['port']
        )

        if raw_host['username']:
            identity = Identity(
                username=raw_host.get('username'),
                is_visible=False,
                label=raw_host.get('username')
            )

            host.ssh_config.identity = identity

        return host

    def create_key(self, identity_paths):
        """Create ssh key instance."""
        with open(identity_paths[0], 'rb') as private_key_file:
            private_key = private_key_file.read()

        with open(identity_paths[1], 'rb') as public_key_file:
            public_key = public_key_file.read()

        return SshKey(
            label='SecureCRT',
            private_key=private_key,
            public_key=public_key
        )
