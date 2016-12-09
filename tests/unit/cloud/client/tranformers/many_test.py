# -*- coding: utf-8 -*-
import tempfile
from pathlib2 import Path
from mock import Mock
from nose.tools import eq_
from ....core.storage.storage_test import StrategyCase
from ..cryptor_test import generate_cryptor, config_factory
from termius.cloud.client.transformers.many import (
    BulkTransformer
)
from termius.core.storage.strategies import (
    RelatedGetStrategy, SyncSaveStrategy
)
from termius.cloud.client.controllers import CryptoController
from termius.account.managers import AccountManager
from termius.core.settings import Config
from termius.core.models.terminal import (
    Host, SshConfig, Identity, SshKey
)

class BulkTransformerTest(StrategyCase):

    maxDiff = None

    get_strategy_class = RelatedGetStrategy
    save_strategy_class = SyncSaveStrategy

    def setUp(self):
        super(BulkTransformerTest, self).setUp()
        self.cryptor = generate_cryptor(**config_factory('1'))
        self.crypto_controller = CryptoController(self.cryptor)
        self.app_tempdir = tempfile.mkdtemp()
        config = Config(Mock(**{'app.directory_path': self.app_tempdir}))
        self.account_manager = AccountManager(config)

    def tearDown(self):
        super(BulkTransformerTest, self).tearDown()
        self._clean_dir(Path(self.app_tempdir))

    def test_create_transformer_sync_key(self):
        self.transformer = BulkTransformer(
            storage=self.storage,
            crypto_controller=self.crypto_controller,
            account_manager=self.account_manager,
        )

        ssh_config = SshConfig()
        identity = Identity(label='identity')
        ssh_key = SshKey(label='ssh_key')
        host = Host(label='host')
        identity.ssh_key = ssh_key.id = self.storage.save(ssh_key).id
        ssh_config.identity = identity.id = self.storage.save(identity).id
        host.ssh_config = ssh_config.id = self.storage.save(ssh_config).id
        host = self.storage.save(host)
        last_synced_data = dict(last_synced='')
        payload = self.transformer.to_payload(last_synced_data)
        self.assertEqual(payload, {
            'host_set': [
                {
                    'label': payload['host_set'][0]['label'],
                    'group': None,
                    'ssh_config': 'sshconfig_set/{}'.format(ssh_config.id),
                    'local_id': host.id,
                    'address': '',
                    'interaction_date': host.interaction_date,
                }
            ],
            'sshconfig_set': [
                {
                    'font_size': None,
                    'keep_alive_packages': None,
                    'charset': None,
                    'identity': 'identity_set/{}'.format(identity.id),
                    'local_id': ssh_config.id,
                    'use_ssh_key': None,
                    'timeout': None,
                    'color_scheme': None,
                    'is_forward_ports': None,
                    'strict_host_key_check': None,
                    'port': None,
                    'startup_snippet': None,
                    'cursor_blink': None
                }
            ],
            'snippet_set': [],
            'last_synced': '',
            'sshkeycrypt_set': [
                {
                    'public_key': '',
                    'private_key': '',
                    'local_id': ssh_key.id,
                    'passphrase': '',
                    'label': payload['sshkeycrypt_set'][0]['label']
                }
            ],
            'group_set': [],
            'tag_set': [],
            'taghost_set': [],
            'pfrule_set': [],
            'delete_sets': {},
            'identity_set': [
                {
                    'username': '',
                    'is_visible': False,
                    'ssh_key': 'sshkeycrypt_set/{}'.format(ssh_key.id),
                    'label': payload['identity_set'][0]['label'],
                    'local_id': identity.id,
                    'password': ''
                }
            ]
        })
        eq_(host.label, self.cryptor.decrypt(
            payload['host_set'][0]['label']
        ))
        eq_(ssh_key.label, self.cryptor.decrypt(
            payload['sshkeycrypt_set'][0]['label']
        ))
        eq_(identity.label, self.cryptor.decrypt(
            payload['identity_set'][0]['label']
        ))

    def test_create_transformer_nosync_key(self):
        self.account_manager.set_settings({
            'synchronize_key': False, 'agent_forwarding': True
        })
        self.transformer = BulkTransformer(
            storage=self.storage,
            crypto_controller=self.crypto_controller,
            account_manager=self.account_manager,
        )

        ssh_config = SshConfig()
        identity = Identity(label='identity')
        ssh_key = SshKey(label='ssh_key')
        host = Host(label='host')
        identity.ssh_key = ssh_key.id = self.storage.save(ssh_key).id
        ssh_config.identity = identity.id = self.storage.save(identity).id
        host.ssh_config = ssh_config.id = self.storage.save(ssh_config).id
        host = self.storage.save(host)
        last_synced_data = dict(last_synced='')
        payload = self.transformer.to_payload(last_synced_data)
        self.assertEqual(payload, {
            'host_set': [
                {
                    'label': payload['host_set'][0]['label'],
                    'group': None,
                    'ssh_config': 'sshconfig_set/{}'.format(ssh_config.id),
                    'local_id': host.id,
                    'address': '',
                    'interaction_date': host.interaction_date,
                }
            ],
            'sshconfig_set': [
                {
                    'font_size': None,
                    'keep_alive_packages': None,
                    'charset': None,
                    'local_id': ssh_config.id,
                    'use_ssh_key': None,
                    'timeout': None,
                    'color_scheme': None,
                    'is_forward_ports': None,
                    'strict_host_key_check': None,
                    'port': None,
                    'startup_snippet': None,
                    'cursor_blink': None
                }
            ],
            'snippet_set': [],
            'last_synced': '',
            'group_set': [],
            'tag_set': [],
            'taghost_set': [],
            'pfrule_set': [],
            'delete_sets': {},
        })
        eq_(host.label, self.cryptor.decrypt(
            payload['host_set'][0]['label']
        ))

    def _clean_dir(self, dir_path):
        [self._clean_dir(i) for i in dir_path.iterdir() if i.is_dir()]
        [i.unlink() for i in dir_path.iterdir() if i.is_file()]
        dir_path.rmdir()
