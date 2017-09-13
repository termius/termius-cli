# -*- coding: utf-8 -*-
"""Module with user data models."""
from datetime import datetime
from operator import attrgetter
from .base import Model, Field


class Tag(Model):
    """Model for tag."""

    fields = {
        'label': Field(str, False, '')
    }
    set_name = 'tag_set'
    crypto_fields = fields


class Snippet(Model):
    """Model for snippet."""

    fields = {
        'label': Field(str, False, ''),
        'script': Field(str, False, ''),
    }
    set_name = 'snippet_set'
    crypto_fields = fields


class SshKey(Model):
    """Model for ssh key."""

    fields = {
        'label': Field(str, False, ''),
        'passphrase': Field(str, False, ''),
        'private_key': Field(str, False, ''),
        'public_key': Field(str, False, ''),
    }
    set_name = 'sshkeycrypt_set'
    crypto_fields = fields
    file_mode = 0o600

    def file_path(self, command):
        """Return path object to private key file."""
        ssh_keys_path = command.config.ssh_key_dir_path
        return ssh_keys_path / self.label


class Identity(Model):
    """Model for identity."""

    fields = {
        'label': Field(str, False, ''),
        'username': Field(str, False, ''),
        'password': Field(str, False, ''),
        'is_visible': Field(str, False, False),
        'ssh_key': Field(SshKey, False, None),
    }
    mergable_fields = {'username', 'password', 'ssh_key'}
    set_name = 'identity_set'
    crypto_fields = {'label', 'username', 'password'}


class SshConfig(Model):
    """Model for ssh config."""

    fields = {
        'port': Field(int, False, None),
        'identity': Field(Identity, False, None),
        'startup_snippet': Field(Snippet, False, None),
        'strict_host_key_check': Field(bool, False, None),
        'use_ssh_key': Field(bool, False, None),
        'timeout': Field(int, False, None),
        'keep_alive_packages': Field(int, False, None),
        'is_forward_ports': Field(bool, False, None),

        'font_size': Field(str, False, None),
        'color_scheme': Field(str, False, None),
        'charset': Field(str, False, None),
        'cursor_blink': Field(bool, False, None),
    }
    mergable_fields = {
        'port',
        'identity',
        'startup_snippet',
        'strict_host_key_check',
        'use_ssh_key',
        'timeout',
        'keep_alive_packages',
        'is_forward_ports',  # not used

        'font_size',
        'color_scheme',
        'charset',
        'cursor_blink',
    }
    set_name = 'sshconfig_set'

    def get_ssh_key(self):
        """Retrieve ssh key instance."""
        return self.identity and self.identity.ssh_key

    def __setattr__(self, name, value):
        """Set attribute, but patch value before assign."""
        patch_method = getattr(self, 'patch_' + name)
        if patch_method:
            value = patch_method(value)

        self[name] = value

    # pylint: disable=no-self-use
    def transform_int(self, value):
        """Transform value to int or return None."""
        try:
            return (value is not None and int(value)) or None
        except ValueError as exception:
            return self.handle_value_error(exception)

    # pylint: disable=no-self-use
    def transform_bool(self, value):
        """Transform value to bool or return None."""
        if value not in ('yes', 'no'):
            if isinstance(value, bool):
                return value
            return None
        return value == 'yes'

    # pylint: disable=no-self-use,unused-argument
    def handle_value_error(self, error):
        """Return default value, when transformation error happens."""
        return None

    patch_port = transform_int
    patch_timeout = transform_int
    patch_keep_alive_packages = transform_int
    patch_use_ssh_key = transform_bool
    patch_strict_host_key_check = transform_bool


# pylint: disable=too-few-public-methods
class SshConfigMixin(object):
    """Mixin to easy and safely get ssh config field."""

    def get_assign_ssh_config(self):
        """Get existed ssh config or create and assign new one."""
        ssh_config = self.ssh_config or SshConfig()
        self.ssh_config = ssh_config
        return ssh_config


class Group(SshConfigMixin, Model):
    """Model for group."""

    fields = {
        'label': Field(str, False, ''),
        'ssh_config': Field(SshConfig, False, None),
    }
    set_name = 'group_set'
    crypto_fields = {'label', }


Group.fields['parent_group'] = Field(Group, False, None)


class Host(SshConfigMixin, Model):
    """Model for host."""

    fields = {
        'label': Field(str, False, ''),
        'address': Field(str, False, ''),
        'group': Field(Group, False, None),
        'ssh_config': Field(SshConfig, False, None),
        'interaction_date': Field(str, False, None),
    }
    set_name = 'host_set'
    crypto_fields = {'label', 'address'}

    def update_interaction_date(self):
        """Set current UTC Time to interaction date."""
        utcnow = datetime.utcnow
        stringifyed_now = utcnow().replace(microsecond=0).isoformat()
        # pylint: disable=attribute-defined-outside-init
        self.interaction_date = stringifyed_now


class TagHost(Model):
    """Model for relation host and tags."""

    fields = {
        'host': Field(Host, False, None),
        'tag': Field(Tag, False, None),
    }
    set_name = 'taghost_set'


class PFRule(Model):
    """Model for port forwarding."""

    fields = {
        'label': Field(str, False, ''),
        'host': Field(Host, False, None),
        'pf_type': Field(str, False, 'L'),
        'bound_address': Field(str, False, ''),
        'local_port': Field(int, False, 22),
        'hostname': Field(str, False, ''),
        'remote_port': Field(int, False, 22),
    }
    set_name = 'pfrule_set'
    crypto_fields = {'label', 'hostname'}

    binding_getter = {
        'Local Rule': attrgetter(
            'bound_address', 'local_port', 'hostname', 'remote_port'
        ),
        'Dynamic Rule': attrgetter('bound_address', 'local_port'),
    }
    binding_getter['Remote Rule'] = binding_getter['Local Rule']

    @property
    def binding(self):
        """Render binding string."""
        bind_gen = self.binding_getter[self.pf_type]
        return ':'.join([str(i) for i in bind_gen(self) if i])


# pylint: disable=invalid-name
clean_order = reversed((
    SshKey, Snippet,
    Identity, SshConfig,
    Tag, Group,
    Host, PFRule,
    TagHost
))
