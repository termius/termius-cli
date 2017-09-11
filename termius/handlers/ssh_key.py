# -*- coding: utf-8 -*-
"""Module with ssh key commands."""
from operator import attrgetter
from pathlib2 import Path
from cached_property import cached_property
from ..core.commands.single import RequiredOptions
from ..core.exceptions import InvalidArgumentException
from ..core.commands import DetailCommand, ListCommand
from ..core.models.terminal import SshKey


# pylint: disable=too-few-public-methods
class SshKeyGeneratorMixin(object):
    """Mixin for create new ssh key from file."""

    # pylint: disable=no-self-use
    def generate_ssh_key_instance(self, path, storage):
        """Generate ssh key from file."""
        private_key_path = Path(path)
        instance = SshKey(
            private_key=private_key_path.read_text(),
            label=private_key_path.name
        )
        self.validate_ssh_key(instance, storage)
        return instance

    def validate_ssh_key(self, instance, storage):
        """Raise an error when any instances exist with same label."""
        with_same_label = storage.filter(
            SshKey, **{'label': instance.label, 'id.ne': instance.id}
        )
        if with_same_label:
            raise InvalidArgumentException('Instances with same label exists.')


class SshKeyCommand(SshKeyGeneratorMixin, DetailCommand):
    """work with an ssh key"""

    model_class = SshKey
    required_options = RequiredOptions(create=('identity_file', 'label'))

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-i', '--identity-file',
            metavar='PRIVATE_KEY', help='private key'
        )
        return parser

    @cached_property
    def fields(self):
        """Return dict with model field serializer per field."""
        _fields = {
            i: attrgetter(i) for i in ('label',)
        }
        _fields['private_key'] = self.get_private_key
        return _fields

    # pylint: disable=no-self-use
    def get_private_key(self, args):
        """Read identity passed to args."""
        return args.identity_file and Path(args.identity_file).read_text()

    def validate(self, instance):
        """Raise an error when any instances exist with same label."""
        self.validate_ssh_key(instance, self.storage)


class SshKeysCommand(ListCommand):
    """list all ssh keys"""

    model_class = SshKey
