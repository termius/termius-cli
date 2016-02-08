# -*- coding: utf-8 -*-
"""Module with user data models."""
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

    def file_path(self, command):
        ssh_keys_path = command.config.ssh_key_dir_path
        return ssh_keys_path / self.label


class SshIdentity(Model):
    """Model for ssh identity."""

    fields = {
        'label': Field(str, False, ''),
        'username': Field(str, False, ''),
        'password': Field(str, False, ''),
        'is_visible': Field(str, False, False),
        'ssh_key': Field(SshKey, False, None),
    }
    mergable_fields = {'username', 'password', 'ssh_key'}
    set_name = 'sshidentity_set'
    crypto_fields = {'label', 'username', 'password'}


class SshConfig(Model):
    """Model for ssh config."""

    fields = {
        'port': Field(int, False, None),
        'color_scheme': Field(str, False, None),
        'charset': Field(str, False, None),
        'font_size': Field(str, False, None),
        'ssh_identity': Field(SshIdentity, False, None),
        'startup_snippet': Field(Snippet, False, None),
    }
    mergable_fields = {
        'port', 'color_scheme',
        'font_size', 'charset',
        'startup_snippet'
    }
    set_name = 'sshconfig_set'


class Group(Model):
    """Model for group."""

    fields = {
        'label': Field(str, False, ''),
        'ssh_config': Field(SshConfig, False, None),
    }
    set_name = 'group_set'
    crypto_fields = {'label', }


Group.fields['parent_group'] = Field(Group, False, None)


class Host(Model):
    """Model for host."""

    fields = {
        'label': Field(str, False, ''),
        'address': Field(str, False, ''),
        'group': Field(Group, False, None),
        'ssh_config': Field(SshConfig, False, None),
    }
    set_name = 'host_set'
    crypto_fields = {'label', 'address'}


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
    crypto_fields = {'label', 'bound_address', 'hostname'}
