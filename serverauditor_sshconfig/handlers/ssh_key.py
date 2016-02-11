# -*- coding: utf-8 -*-
"""Module with ssh key commands."""
from pathlib2 import Path
from ..core.commands.single import RequiredOptions
from ..core.commands import DetailCommand, ListCommand
from ..core.models.terminal import SshKey


# pylint: disable=too-few-public-methods
class SshKeyGeneratorMixin(object):
    """Mixin for create new ssh key from file."""

    # pylint: disable=no-self-use
    def generate_ssh_key_instance(self, path):
        """Generate ssh key from file."""
        private_key_path = Path(path)
        return SshKey(
            private_key=private_key_path.read_text(),
            label=private_key_path.name
        )


class SshKeyCommand(SshKeyGeneratorMixin, DetailCommand):
    """Operate with Host object."""

    model_class = SshKey
    required_options = RequiredOptions(create=('identity_file',))

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-i', '--identity-file',
            metavar='PRIVATE_KEY', help='Private key.'
        )
        return parser

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        if instance:
            ssh_key = instance
            if args.identity_file:
                with open(args.identity_file, 'r') as _file:
                    ssh_key.private_key = _file.read()
        else:
            ssh_key = self.generate_ssh_key_instance(args.identity_file)

        if args.label:
            ssh_key.label = args.label
        return ssh_key


class SshKeysCommand(ListCommand):
    """Manage ssh key objects."""

    model_class = SshKey
