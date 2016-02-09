# -*- coding: utf-8 -*-
import tempfile
from six import integer_types
from mock import patch, Mock
from unittest import TestCase
from serverauditor_sshconfig.core.models.terminal import (
    Host, SshConfig, SshIdentity, SshKey, Group
)
from serverauditor_sshconfig.core.exceptions import DoesNotExistException
from serverauditor_sshconfig.core.storage.strategies import (
    GetStrategy, SaveStrategy, RelatedGetStrategy, RelatedSaveStrategy
)


class StrategyCase(TestCase):

    save_strategy_class = None
    get_strategy_class = None

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.storage_file_patch = patch(
            'serverauditor_sshconfig.core.storage.ApplicationStorage.path',
            self.tempfile.name
        )

        self.assertIsNotNone(self.save_strategy_class)
        self.assertIsNotNone(self.get_strategy_class)

        from serverauditor_sshconfig.core.storage import ApplicationStorage

        self.storage = ApplicationStorage(
            Mock(**{'app.directory_path.return_value': 'TestCase'}),
            save_strategy=self.save_strategy_class,
            get_strategy=self.get_strategy_class
        )

        self.storage_file_patch.start()

    def tearDown(self):
        self.storage_file_patch.stop()
        self.tempfile.close()


class IDStrategyCase(StrategyCase):

    save_strategy_class = SaveStrategy
    get_strategy_class = GetStrategy

    def setUp(self):
        super(IDStrategyCase, self).setUp()
        self.group = Group(label='host_test')
        self.host = Host(label='host_test')
        self.sshconfig = SshConfig(port=2)
        self.sshidentity = SshIdentity(username='username')
        self.sshkey = SshKey(label='label')

    def test_save_strategy(self):
        saved_sshkey = self.storage.save(self.sshkey)
        self.assertIsNotNone(saved_sshkey.id)
        self.sshidentity.ssh_key = saved_sshkey.id

        saved_sshidentity = self.storage.save(self.sshidentity)
        self.assertIsNotNone(saved_sshidentity.id)
        self.assertIsInstance(saved_sshidentity.ssh_key, integer_types)
        self.sshconfig.ssh_identity = saved_sshidentity.id

        saved_sshconfig = self.storage.save(self.sshconfig)
        self.assertIsNotNone(saved_sshconfig.id)
        self.assertIsInstance(saved_sshconfig.ssh_identity, integer_types)
        self.host.ssh_config = saved_sshconfig.id
        saved_group = self.storage.save(self.group)
        self.assertIsNotNone(saved_group.id)
        self.host.group = saved_group.id

        saved_host = self.storage.save(self.host)
        self.assertIsInstance(saved_host.ssh_config, integer_types)
        self.assertIsInstance(saved_host.group, integer_types)
        self.assertIsNotNone(saved_host.id)

    def test_get_strategy(self):
        saved_sshkey = self.storage.save(self.sshkey)
        self.sshidentity.ssh_key = saved_sshkey.id

        saved_sshidentity = self.storage.save(self.sshidentity)
        self.sshconfig.ssh_identity = saved_sshidentity.id

        saved_sshconfig = self.storage.save(self.sshconfig)
        self.host.ssh_config = saved_sshconfig.id
        saved_group = self.storage.save(self.group)
        self.host.group = saved_group.id

        saved_host = self.storage.save(self.host)

        got_sshkey = self.storage.get(SshKey, id=saved_sshkey.id)
        self.assertEqual(got_sshkey.id, saved_sshkey.id)
        self.assertEqual(got_sshkey.label, self.sshkey.label)

        got_sshidentity = self.storage.get(
            SshIdentity, id=saved_sshidentity.id
        )
        self.assertEqual(got_sshidentity.id, saved_sshidentity.id)
        self.assertEqual(got_sshidentity.label, self.sshidentity.label)
        self.assertEqual(got_sshidentity.ssh_key, saved_sshkey.id)

        got_sshconfig = self.storage.get(
            SshConfig, id=saved_sshconfig.id
        )
        self.assertEqual(got_sshconfig.id, saved_sshconfig.id)
        self.assertEqual(got_sshconfig.port, self.sshconfig.port)
        self.assertEqual(got_sshconfig.ssh_identity, saved_sshidentity.id)

        got_group = self.storage.get(Group, id=saved_group.id)
        self.assertEqual(got_group.id, saved_group.id)
        self.assertEqual(got_group.label, self.group.label)

        got_host = self.storage.get(Host, id=saved_host.id)
        self.assertEqual(got_host.id, saved_host.id)
        self.assertEqual(got_host.label, self.host.label)
        self.assertEqual(got_host.ssh_config, saved_sshconfig.id)
        self.assertEqual(got_host.group, saved_group.id)

    def test_get_not_existed_strategy(self):
        with self.assertRaises(DoesNotExistException):
            self.storage.get(Host, id=0)

    def test_get_all_strategy(self):
        saved_sshkey = self.storage.save(self.sshkey)
        self.sshidentity.ssh_key = saved_sshkey.id

        saved_sshidentity = self.storage.save(self.sshidentity)
        self.sshconfig.ssh_identity = saved_sshidentity.id

        saved_sshconfig = self.storage.save(self.sshconfig)
        self.host.ssh_config = saved_sshconfig.id
        saved_group = self.storage.save(self.group)
        self.host.group = saved_group.id

        saved_host = self.storage.save(self.host)

        got_sshkeys = self.storage.get_all(SshKey)
        self.assertEqual(len(got_sshkeys), 1)
        got_sshkey = got_sshkeys[0]
        self.assertEqual(got_sshkey.id, saved_sshkey.id)
        self.assertEqual(got_sshkey.label, self.sshkey.label)

        got_sshidentitys = self.storage.get_all(SshIdentity)
        self.assertEqual(len(got_sshidentitys), 1)
        got_sshidentity = got_sshidentitys[0]
        self.assertEqual(got_sshidentity.id, saved_sshidentity.id)
        self.assertEqual(got_sshidentity.label, self.sshidentity.label)
        self.assertEqual(got_sshidentity.ssh_key, saved_sshkey.id)

        got_sshconfigs = self.storage.get_all(SshConfig)
        self.assertEqual(len(got_sshconfigs), 1)
        got_sshconfig = got_sshconfigs[0]
        self.assertEqual(got_sshconfig.id, saved_sshconfig.id)
        self.assertEqual(got_sshconfig.port, self.sshconfig.port)
        self.assertEqual(got_sshconfig.ssh_identity, saved_sshidentity.id)

        got_groups = self.storage.get_all(Group)
        self.assertEqual(len(got_sshconfigs), 1)
        got_group = got_groups[0]
        self.assertEqual(got_group.id, saved_group.id)
        self.assertEqual(got_group.label, self.group.label)

        got_hosts = self.storage.get_all(Host)
        self.assertEqual(len(got_hosts), 1)
        got_host = got_hosts[0]
        self.assertEqual(got_host.id, saved_host.id)
        self.assertEqual(got_host.label, self.host.label)
        self.assertEqual(got_host.ssh_config, saved_sshconfig.id)
        self.assertEqual(got_host.group, saved_group.id)


class RelatedStrategyCase(StrategyCase):

    save_strategy_class = RelatedSaveStrategy
    get_strategy_class = RelatedGetStrategy

    def setUp(self):
        super(RelatedStrategyCase, self).setUp()
        self.group = Group(label='host_test')
        self.host = Host(label='host_test')
        self.sshconfig = SshConfig(port=2)
        self.sshidentity = SshIdentity(username='username')
        self.sshkey = SshKey(label='label')

    def test_save_strategy(self):
        self.sshidentity.ssh_key = self.sshkey
        self.sshconfig.ssh_identity = self.sshidentity
        self.host.ssh_config = self.sshconfig
        self.host.group = self.group

        saved_host = self.storage.save(self.host)

        self.assertIsNotNone(saved_host.id)
        self.assertIsInstance(saved_host.ssh_config, integer_types)
        self.assertIsInstance(saved_host.group, integer_types)

        saved_group = self.storage.get(Group, id=saved_host.group)
        self.assertIsNotNone(saved_group.id)

        saved_sshconfig = self.storage.get(SshConfig, id=saved_host.ssh_config)
        self.assertIsNotNone(saved_sshconfig.id)
        self.assertIsInstance(saved_sshconfig.ssh_identity, SshIdentity)
        self.assertIsInstance(saved_sshconfig.ssh_identity.id, integer_types)

        saved_sshidentity = self.storage.get(
            SshIdentity, id=saved_sshconfig.ssh_identity.id
        )
        self.assertIsNotNone(saved_sshidentity.id)
        self.assertIsInstance(saved_sshidentity.ssh_key, SshKey)
        self.assertIsInstance(saved_sshidentity.ssh_key.id, integer_types)

        saved_sshkey = self.storage.get(
            SshKey, id=saved_sshidentity.ssh_key.id
        )
        self.assertIsNotNone(saved_sshkey.id)

    def test_save_2_times(self):
        for _ in range(2):
            self.test_save_strategy()

    def test_get_strategy(self):
        self.sshidentity.ssh_key = self.sshkey
        self.sshconfig.ssh_identity = self.sshidentity
        self.host.ssh_config = self.sshconfig
        self.host.group = self.group

        saved_host = self.storage.save(self.host)

        got_host = self.storage.get(Host, id=saved_host.id)

        self.assertIsNotNone(got_host.id)
        self.assertEqual(got_host.label, self.host.label)

        self.assertIsInstance(got_host.group, Group)
        self.assertIsInstance(got_host.group.id, integer_types)
        self.assertEqual(got_host.group.label, self.group.label)

        self.assertIsInstance(got_host.ssh_config, SshConfig)
        self.assertIsInstance(got_host.ssh_config.id, integer_types)
        self.assertEqual(got_host.ssh_config.port, self.sshconfig.port)

        self.assertIsInstance(got_host.ssh_config.ssh_identity, SshIdentity)
        self.assertIsInstance(got_host.ssh_config.ssh_identity.id, integer_types)
        self.assertEqual(got_host.ssh_config.ssh_identity.label,
                         self.sshidentity.label)

        self.assertIsInstance(got_host.ssh_config.ssh_identity.ssh_key, SshKey)
        self.assertIsInstance(got_host.ssh_config.ssh_identity.ssh_key.id,
                              integer_types)
        self.assertEqual(got_host.ssh_config.ssh_identity.ssh_key.label,
                         self.sshkey.label)

        got_group = self.storage.get(
            Group, id=got_host.group.id
        )

        self.assertIsNotNone(got_group.id)
        self.assertEqual(got_group.label, self.group.label)

        got_sshconfig = self.storage.get(SshConfig, id=got_host.ssh_config.id)

        self.assertIsNotNone(got_sshconfig.id)
        self.assertEqual(got_sshconfig.port, self.sshconfig.port)

        self.assertIsInstance(got_sshconfig.ssh_identity, SshIdentity)
        self.assertIsInstance(got_sshconfig.ssh_identity.id, integer_types)
        self.assertEqual(got_sshconfig.ssh_identity.label,
                         self.sshidentity.label)

        self.assertIsInstance(got_sshconfig.ssh_identity.ssh_key, SshKey)
        self.assertIsInstance(got_sshconfig.ssh_identity.ssh_key.id, integer_types)
        self.assertEqual(got_sshconfig.ssh_identity.ssh_key.label,
                         self.sshkey.label)

        got_sshidentity = self.storage.get(
            SshIdentity, id=got_sshconfig.ssh_identity.id
        )

        self.assertIsNotNone(got_sshidentity.id)
        self.assertEqual(got_sshidentity.label, self.sshidentity.label)

        self.assertIsInstance(got_sshidentity.ssh_key, SshKey)
        self.assertIsInstance(got_sshidentity.ssh_key.id, integer_types)
        self.assertEqual(got_sshidentity.ssh_key.label, self.sshkey.label)

        got_sshkey = self.storage.get(
            SshKey, id=got_sshidentity.ssh_key.id
        )

        self.assertIsNotNone(got_sshkey.id)
        self.assertEqual(got_sshkey.label, self.sshkey.label)

    def test_get_not_existed_strategy(self):
        with self.assertRaises(DoesNotExistException):
            self.storage.get(Host, id=0)

    def test_get_all_strategy(self):
        self.sshidentity.ssh_key = self.sshkey
        self.sshconfig.ssh_identity = self.sshidentity
        self.host.ssh_config = self.sshconfig
        self.host.group = self.group

        saved_host = self.storage.save(self.host)

        got_hosts = self.storage.get_all(Host)
        self.assertEqual(len(got_hosts), 1)
        got_host = got_hosts[0]

        self.assertIsNotNone(got_host.id)
        self.assertEqual(got_host.label, self.host.label)

        self.assertIsInstance(got_host.group, Group)
        self.assertIsInstance(got_host.group.id, integer_types)
        self.assertEqual(got_host.group.label, self.group.label)

        self.assertIsInstance(got_host.ssh_config, SshConfig)
        self.assertIsInstance(got_host.ssh_config.id, integer_types)
        self.assertEqual(got_host.ssh_config.port, self.sshconfig.port)

        self.assertIsInstance(got_host.ssh_config.ssh_identity, SshIdentity)
        self.assertIsInstance(got_host.ssh_config.ssh_identity.id, integer_types)
        self.assertEqual(got_host.ssh_config.ssh_identity.label,
                         self.sshidentity.label)

        self.assertIsInstance(got_host.ssh_config.ssh_identity.ssh_key, SshKey)
        self.assertIsInstance(got_host.ssh_config.ssh_identity.ssh_key.id,
                              integer_types)
        self.assertEqual(got_host.ssh_config.ssh_identity.ssh_key.label,
                         self.sshkey.label)

        got_groups = self.storage.get_all(Group)
        self.assertEqual(len(got_groups), 1)
        got_group = got_groups[0]

        self.assertIsNotNone(got_group.id)
        self.assertEqual(got_group.label, self.group.label)

        got_sshconfigs = self.storage.get_all(SshConfig)
        self.assertEqual(len(got_sshconfigs), 1)
        got_sshconfig = got_sshconfigs[0]

        self.assertIsNotNone(got_sshconfig.id)
        self.assertEqual(got_sshconfig.port, self.sshconfig.port)

        self.assertIsInstance(got_sshconfig.ssh_identity, SshIdentity)
        self.assertIsInstance(got_sshconfig.ssh_identity.id, integer_types)
        self.assertEqual(got_sshconfig.ssh_identity.label,
                         self.sshidentity.label)

        self.assertIsInstance(got_sshconfig.ssh_identity.ssh_key, SshKey)
        self.assertIsInstance(got_sshconfig.ssh_identity.ssh_key.id, integer_types)
        self.assertEqual(got_sshconfig.ssh_identity.ssh_key.label,
                         self.sshkey.label)

        got_sshidentities = self.storage.get_all(SshIdentity)
        self.assertEqual(len(got_sshidentities), 1)
        got_sshidentity = got_sshidentities[0]

        self.assertIsNotNone(got_sshidentity.id)
        self.assertEqual(got_sshidentity.label, self.sshidentity.label)

        self.assertIsInstance(got_sshidentity.ssh_key, SshKey)
        self.assertIsInstance(got_sshidentity.ssh_key.id, integer_types)
        self.assertEqual(got_sshidentity.ssh_key.label, self.sshkey.label)

        got_sshkies = self.storage.get_all(SshKey)
        self.assertEqual(len(got_sshkies), 1)
        got_sshkey = got_sshkies[0]

        self.assertIsNotNone(got_sshkey.id)
        self.assertEqual(got_sshkey.label, self.sshkey.label)
