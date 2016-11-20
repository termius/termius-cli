# -*- coding: utf-8 -*-
import os.path
from mock import patch, MagicMock
from six import StringIO
from nose.tools import eq_
from termius.sync.providers.ssh import SSHService
from termius.core.models.terminal import (
    Host, SshConfig, Identity, SshKey
)


@patch('termius.sync.providers.ssh.Path')
def test_empty_sshconfig(mockpath):
    mockpath.return_value.open.return_value.__enter__.return_value = StringIO()
    service = SSHService(None, '')
    ssh_hosts = service.hosts()
    eq_(ssh_hosts, [])


@patch('termius.sync.providers.ssh.Path')
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
    service = SSHService(None, '')
    ssh_hosts = service.hosts()
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


@patch('termius.sync.providers.ssh.Path')
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
    service = SSHService(None, '')
    ssh_hosts = service.hosts()
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


@patch('termius.sync.providers.ssh.Path')
def test_single_sshconfig_with_keys(mockpath):
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

    mockpath.side_effect = fake_files.generate_path_obj

    service = SSHService(None, '')
    ssh_hosts = service.hosts()
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
        mock.open.return_value.__enter__.side_effect = lambda: StringIO(self.files[path])
        mock.read_text.side_effect = lambda: self.files[path]
        return mock
