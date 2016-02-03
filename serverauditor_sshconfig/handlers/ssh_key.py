# -*- coding: utf-8 -*-
"""Module with ssh key commands."""
import os.path
from ..core.exceptions import ArgumentRequiredException
from ..core.commands import DetailCommand, ListCommand
from ..core.models.terminal import SshKey


class SshKeyGeneratorMixin(object):
    def generate_ssh_key_instance(self, path):
        with open(path, 'r') as _file:
            content = _file.read()
        label = os.path.basename(path)
        return SshKey(private_key=content, label=label)


class SshKeyCommand(SshKeyGeneratorMixin, DetailCommand):
    """Operate with Host object."""

    allowed_operations = DetailCommand.all_operations
    model_class = SshKey

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(SshKeyCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-i', '--identity-file',
            metavar='PRIVATE_KEY', help='Private key.'
        )
        return parser

    def create(self, parsed_args):
        """Handle create new instance command."""
        if not parsed_args.identity_file:
            raise ArgumentRequiredException('Identity file is required.')

        self.create_instance(parsed_args)

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        if instance:
            ssh_key = instance
        else:
            ssh_key = self.generate_ssh_key_instance(args.identity_file)

        if args.label:
            ssh_key.label = args.label
        return ssh_key


class SshKeysCommand(ListCommand):
    """Manage ssh key objects."""

    model_class = SshKey

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        instances = self.storage.get_all(self.model_class)
        return self.prepare_result(instances)
