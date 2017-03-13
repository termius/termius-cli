# -*- coding: utf-8 -*-
from unittest import TestCase

from mock import Mock, mock
from nose.tools import eq_, assert_raises
from six.moves import configparser

from termius.account.managers import AccountManager


class AccountManagerTest(TestCase):
    def test_get_yes_settings(self):
        manager = self.get_manager(lambda *args, **kwargs: 'yes')
        settings = manager.get_settings()
        eq_(settings, {
            'synchronize_key': True,
            'agent_forwarding': True
        })

    def test_fail_settings(self):
        manager = self.get_manager(KeyError)
        with assert_raises(KeyError):
            manager.get_settings()

    def get_manager(self, config_side_effect):
        config_mock = Mock(**{'get_safe.side_effect': config_side_effect})
        return AccountManager(config_mock)

    def test_get_analytics_id_when_exists(self):
        aid = 'id'
        config_mock = Mock()
        config_mock.get.return_value = aid

        manager = AccountManager(config_mock)
        self.assertEquals(aid, manager.analytics_id)

        config_mock.get.assert_called_once_with('User', 'analytics_id')

    @mock.patch('termius.account.managers.uuid')
    def test_get_analytics_id_when_not_exists(self, uuid):
        aid = 'id'
        uuid.uuid4.return_value = aid

        config_mock = Mock()
        config_mock.get.side_effect = configparser.NoSectionError('msg')

        manager = AccountManager(config_mock)
        self.assertEquals(aid, manager.analytics_id)

        config_mock.set.assert_called_once_with('User', 'analytics_id', aid)
        config_mock.write.assert_called_once()
