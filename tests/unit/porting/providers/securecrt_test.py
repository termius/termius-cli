from io import BytesIO
from unittest import TestCase

from mock import patch, mock_open, call

from termius.core.models.terminal import Host, Group, SshConfig, Identity, \
    SshKey
from termius.porting.providers.securecrt.provider import\
    SecureCRTPortingProvider


class SecureCRTProviderTest(TestCase):
    def test_tree_parsing(self):
        securecrt_config = """<?xml version="1.0" encoding="UTF-8"?>
    <VanDyke version="3.0">
        <key name="Sessions">
            <key name="host0">
                <dword name="[SSH2] Port">0</dword>
                <string name="Hostname">addr0</string>
                <string name="Username">user0</string>
            </key>
            <key name="hosts">
                <key name="folder0">
                    <key name="host1">
                        <dword name="[SSH2] Port">1</dword>
                        <string name="Hostname">addr1</string>
                        <string name="Username">user1</string>
                    </key>
                </key>
                <key name="folder1">
                    <key name="host2">
                        <dword name="[SSH2] Port">2</dword>
                        <string name="Hostname">addr2</string>
                        <string name="Username">user2</string>
                    </key>
                    <key name="serial">
                        <string name="Username">serial_user</string>
                    </key>
                </key>
            </key>
        </key>
    </VanDyke>
    """
        xml_path = '/some/path/securecrt.xml'
        root_group = Group(label='SecureCRT')
        hosts_folder = Group(
            label='hosts', parent_group=root_group
        )
        expected = [
            Host(
                label='host2',
                address='addr2',
                group=Group(label='folder1', parent_group=hosts_folder),
                ssh_config=SshConfig(
                    port='2',
                    identity=Identity(
                        label='user2', username='user2', is_visible=False
                    )
                )
            ),
            Host(
                label='host1',
                address='addr1',
                group=Group(label='folder0', parent_group=hosts_folder),
                ssh_config=SshConfig(
                    port='1',
                    identity=Identity(
                        label='user1', username='user1', is_visible=False
                    )
                )
            ),
            Host(
                label='host0', address='addr0', group=root_group,
                ssh_config=SshConfig(
                    port='0',
                    identity=Identity(
                        label='user0', username='user0', is_visible=False
                    )
                )
            )
        ]

        with patch('xml.etree.ElementTree.open',
                   mock_open(read_data=securecrt_config)) as mocked_xml:
            service = SecureCRTPortingProvider(xml_path, None, '')
            hosts = service.provider_hosts()
            mocked_xml.assert_called_once_with(xml_path, 'rb')
            self.assertEquals(
                self.sort_hosts(hosts),
                self.sort_hosts(expected)
            )

    def test_ssh2_identity_parsing(self):
        public_key = b'public'
        private_key = b'private'
        xml_path = '/some/path/securecrt.xml'

        root_group = Group(
            label='SecureCRT',
            ssh_config=SshConfig(
                identity=Identity(
                    label='SecureCRT',
                    is_visible=False,
                    ssh_key=SshKey(
                        label='SecureCRT',
                        private_key=private_key,
                        public_key=public_key
                    )
                )
            )
        )
        securecrt_config = """<?xml version="1.0" encoding="UTF-8"?>
            <VanDyke version="3.0">
                <key name="Sessions">
                    <key name="host0">
                        <dword name="[SSH2] Port">0</dword>
                        <string name="Hostname">addr0</string>
                        <string name="Username">user0</string>
                    </key>
                </key>
                <key name="SSH2">
                    <string name="Identity Filename V2">/Users/termius/folder/key.pub::rawkey</string>
                </key>
            </VanDyke>
            """
        expected = [
            Host(
                label='host0', group=root_group, address='addr0',
                ssh_config=SshConfig(port='0',
                    identity=Identity(
                        label='user0',
                        is_visible=False,
                        username='user0'
                    )
                )
            )
        ]
        expected_calls = [
            call('/Users/termius/folder/key', 'rb'),
            call('/Users/termius/folder/key.pub', 'rb')
        ]

        with patch('xml.etree.ElementTree.open',
                   mock_open(read_data=securecrt_config)) as mocked_xml:

            with patch('termius.porting.providers.securecrt.provider.open',
                       mock_open(read_data='')) as mocked_open:
                service = SecureCRTPortingProvider(xml_path, None, '')
                mocked_open.side_effect = [
                    BytesIO(private_key), BytesIO(public_key)
                ]
                hosts = service.provider_hosts()
                self.assertEquals(
                    self.sort_hosts(hosts),
                    self.sort_hosts(expected)
                )
                mocked_xml.assert_called_once_with(xml_path, 'rb')
                mocked_open.assert_has_calls(expected_calls)

    def sort_hosts(self, hosts):
        return sorted(hosts, key=lambda host: host['address'])