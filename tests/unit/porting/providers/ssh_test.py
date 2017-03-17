# -*- coding: utf-8 -*-
import os.path
from mock import patch, MagicMock
from six import StringIO
from nose.tools import eq_
from termius.porting.providers.ssh.provider import SSHPortingProvider
from termius.core.models.terminal import (
    Host, SshConfig, Identity, SshKey
)


@patch('termius.porting.providers.ssh.provider.Path')
def test_empty_sshconfig(mockpath):
    mockpath.return_value.open.return_value.__enter__.return_value = StringIO()
    service = SSHPortingProvider(None, '')
    ssh_hosts = service.provider_hosts()
    eq_(ssh_hosts, [])


@patch('termius.porting.providers.ssh.provider.Path')
def test_single_sshconfig(mockpath):
    mockpath.return_value.open.return_value.__enter__.return_value = StringIO(
        """
Host firstone
    HostName localhost
    User ubuntu
    ServerAliveInterval 100
    ServerAliveCountMax 3
    IdentitiesOnly yes
    StrictHostKeyChecking no
        """
    )
    service = SSHPortingProvider(None, '')
    ssh_hosts = service.provider_hosts()
    eq_(ssh_hosts, [
        Host(
            label='firstone',
            address='localhost',
            ssh_config=SshConfig(
                port=None,
                timeout=100,
                keep_alive_packages=3,
                use_ssh_key=True,
                strict_host_key_check=False,
                identity=Identity(
                    username='ubuntu',
                    ssh_key=None
                )
            )
        )
    ])


@patch('termius.porting.providers.ssh.provider.Path')
def test_single_sshconfig_with_fnmatch(mockpath):
    mockpath.return_value.open.return_value.__enter__.return_value = StringIO(
        """
Host ?i*one
    Port 2022

Host firstone
    HostName localhost
    User ubuntu
        """
    )
    service = SSHPortingProvider(None, '')
    ssh_hosts = service.provider_hosts()
    eq_(ssh_hosts, [
        Host(
            label='firstone',
            address='localhost',
            ssh_config=SshConfig(
                port=2022,
                timeout=None,
                keep_alive_packages=None,
                use_ssh_key=None,
                strict_host_key_check=None,
                identity=Identity(
                    username='ubuntu',
                    ssh_key=None
                )
            )
        )
    ])


@patch('termius.porting.providers.ssh.provider.Path')
@patch('termius.porting.providers.ssh.adapter.Path')
def test_single_sshconfig_with_keys(path_in_providers, path_in_adapters):
    sshconfig_content = """
Host firstone
    HostName localhost
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
    IdentityFile ~/.ssh/id_dsa
    """
    private_key_content = 'private_key'
    fake_files = FakePathsObj(**{
        '~/.ssh/config': sshconfig_content,
        '~/.ssh/id_rsa': private_key_content
    })

    path_in_providers.side_effect = fake_files.generate_path_obj
    path_in_adapters.side_effect = fake_files.generate_path_obj

    service = SSHPortingProvider(None, '')
    ssh_hosts = service.provider_hosts()
    eq_(ssh_hosts, [
        Host(
            label='firstone',
            address='localhost',
            ssh_config=SshConfig(
                port=None,
                timeout=None,
                keep_alive_packages=None,
                use_ssh_key=None,
                strict_host_key_check=None,
                identity=Identity(
                    username='ubuntu',
                    ssh_key=SshKey(
                        label='id_rsa',
                        private_key='private_key'
                    )
                )
            )
        )
    ])


class FakePathsObj(object):
    def __init__(self, **kwargs):
        self.files = {
            os.path.expanduser(i): content
            for i, content in kwargs.items()
            }

    def generate_path_obj(self, path):
        mock = MagicMock()
        mock.name = os.path.basename(path)
        path = os.path.expanduser(path)
        mock.is_file.return_value = path in self.files
        mock.open.return_value.__enter__.side_effect = lambda: StringIO(
            self.files[path])
        mock.read_text.side_effect = lambda: self.files[path]
        return mock
