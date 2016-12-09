# -*- coding: utf-8 -*-
from mock import Mock
from nose.tools import eq_, assert_raises
from termius.account.managers import AccountManager


def test_get_yes_settings():
    manager = get_manager(lambda *args, **kwargs: 'yes')
    settings = manager.get_settings()
    eq_(settings, {
        'synchronize_key': True,
        'agent_forwarding': True
    })


def test_fail_settings():
    manager = get_manager(KeyError)
    with assert_raises(KeyError):
        manager.get_settings()


def get_manager(config_side_effect):
    config_mock = Mock(**{'get_safe.side_effect': config_side_effect})
    return AccountManager(config_mock)
