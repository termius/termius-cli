# -*- coding: utf-8 -*-
"""Module for identity command."""
from operator import attrgetter, truth
from functools import partial
from cached_property import cached_property
from ..core.commands import DetailCommand, ListCommand
from ..core.models.terminal import Identity, SshKey
from ..core.commands.single import RequiredOptions
from ..core.exceptions import InvalidArgumentException, DoesNotExistException
from .ssh_key import SshKeyGeneratorMixin


class IdentityCommand(SshKeyGeneratorMixin, DetailCommand):
    """work with an identity"""

    model_class = Identity
    required_options = RequiredOptions(create=('label',))

    @cached_property
    def fields(self):
        """Return dictionary of args serializers to models field."""
        _fields = {
            i: attrgetter(i) for i in ('label', 'username', 'password')
        }
        _fields['ssh_key'] = self.get_ssh_key_field
        _fields['is_visible'] = partial(truth)
        return _fields

    def get_ssh_key_field(self, args):
        """Return ssh key instance or None.

        Retrieve per ssh_key argument or create new one using identity file.
        """
        if args.identity_file and args.ssh_key:
            raise InvalidArgumentException(
                'You can not use ssh key and identity file together!'
            )
        if args.identity_file:
            return self.generate_ssh_key_instance(
                args.identity_file, self.storage
            )
        if args.ssh_key:
            return self.get_safely_instance(SshKey, args.ssh_key)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-u', '--username',
            metavar='USERNAME', help='username for ssh authentication'
        )
        parser.add_argument(
            '-p', '--password',
            metavar='PASSWORD', help='password for ssh authentication'
        )
        parser.add_argument(
            '-i', '--identity-file',
            metavar='FILE', help='select FILE as private key'
        )
        parser.add_argument(
            '-k', '--ssh-key',
            metavar='ID or NAME', help='define ssh key with ID or NAME'
        )
        return parser

    def get_objects(self, ids__names):
        """Get model list.

        Models will match id and label with passed ids__names list.
        """
        instances = super(IdentityCommand, self).get_objects(ids__names)
        visible_instances = [i for i in instances if i.is_visible]
        if not visible_instances:
            raise DoesNotExistException("There aren't any instance.")
        return instances


class IdentitiesCommand(ListCommand):
    """list all identities"""

    model_class = Identity

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        instances = self.storage.filter(self.model_class, is_visible=True)
        return self.prepare_result(instances)
