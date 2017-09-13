# -*- coding: utf-8 -*-
"""Module with Sshconfig's args helper."""
from operator import attrgetter, not_
from functools import partial
from cached_property import cached_property
from ..core.models.terminal import SshConfig, Identity, Snippet
from ..core.exceptions import InvalidArgumentException
from ..core.commands.mixins import ArgModelSerializerMixin
from .ssh_key import SshKeyGeneratorMixin


class IdentityArgs(SshKeyGeneratorMixin, ArgModelSerializerMixin, object):
    """Class for serializing identity instance."""

    model_class = Identity

    def __init__(self, command):
        """Contruct new ssh config argument helper."""
        self.command = command

    @cached_property
    def fields(self):
        """Return dictionary of args serializers to models field."""
        _fields = {
            i: attrgetter(i) for i in ('username', 'password')
        }
        _fields['ssh_key'] = self.get_ssh_key_field
        _fields['is_visible'] = partial(not_)
        return _fields

    def get_ssh_key_field(self, args):
        """Create ssh key instance from args."""
        return args.identity_file and self.generate_ssh_key_instance(
            args.identity_file, self.command.storage
        )

    # pylint: disable=no-self-use
    def add_args(self, parser):
        """Add identity args to argparser."""
        parser.add_argument(
            '-u', '--username', metavar='USERNAME',
            help='USERNAME for ssh authentication'
        )
        parser.add_argument(
            '-P', '--password', metavar='PASSWORD',
            help='PASSWORD for ssh authentication'
        )
        parser.add_argument(
            '-i', '--identity-file', metavar='FILE',
            help=('select FILE as private key')
        )
        return parser


class SshConfigArgs(ArgModelSerializerMixin, object):
    """Class for ssh config argument adding and serializing."""

    model_class = SshConfig

    def __init__(self, command):
        """Contruct new ssh config argument helper."""
        self.command = command
        self.identity_args = IdentityArgs(self.command)

    @cached_property
    def fields(self):
        """Return dictionary of args serializers to models field."""
        _fields = {
            i: attrgetter(i) for i in (
                'port', 'strict_host_key_check', 'use_ssh_key',
                'keep_alive_packages', 'timeout',
            )
        }
        _fields['startup_snippet'] = self.command.get_safely_instance_partial(
            Snippet, 'snippet'
        )
        return _fields

    # pylint: disable=no-self-use
    def add_agrs(self, parser):
        """Add to arg parser ssh config options."""
        parser.add_argument(
            '-p', '--port',
            type=int, metavar='PORT',
            help='assign PORT to ssh config'
        )
        parser.add_argument(
            '-s', '--snippet', metavar='SNIPPET',
            help='assign SNIPPET to ssh config'
        )
        parser.add_argument(
            '--identity',
            metavar='IDENTITY', help="assign IDENTITY to ssh config"
        )
        parser.add_argument(
            '-S', '--strict-host-key-check', type=str,
            choices=('yes', 'no'),
            help='check host public key by force (enable/disable)'
        )
        parser.add_argument(
            '--use-ssh-key', type=str,
            choices=('yes', 'no'),
            help='use public key by force (enable/disable)'
        )
        parser.add_argument(
            '-k', '--keep-alive-packages',
            type=int, metavar='PACKAGES_COUNT',
            help='define ServerAliveCountMax in the ssh config'
        )
        parser.add_argument(
            '-T', '--timeout',
            type=int, metavar='SECONDS',
            help='define ServerAliveInterval in the ssh config'
        )

        self.identity_args.add_args(parser)
        return parser

    def serialize_args(self, args, instance=None):
        """Change implementation to add relation serialization."""
        instance = super(SshConfigArgs, self).serialize_args(args, instance)
        instance.identity = self.serialize_identity(args, instance)
        return instance

    def serialize_identity(self, args, instance):
        """Update identity field and clean old one."""
        old = instance and instance.identity
        new = self.serialize_identity_field(args, old)
        if new and old and new.is_visible and not old.is_visible:
            self.clean_invisible_identity(old)
        return new

    def clean_invisible_identity(self, identity):
        """Stub cleaning identity."""
        self.command.storage.delete(identity)

    def serialize_identity_field(self, args, instance):
        """Serialize identity."""
        if (args.password or args.username) and args.identity:
            raise InvalidArgumentException()

        if args.identity:
            identity = self.command.get_relation(
                Identity, args.identity
            )
            if not identity.is_visible:
                self.command.fail_not_exist(Identity)
            return identity
        instance = instance and (not instance.is_visible and instance) or None
        return self.identity_args.serialize_args(args, instance)
