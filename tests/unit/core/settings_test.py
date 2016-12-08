# -*- coding: utf-8 -*-
import os
from mock import Mock
from pathlib2 import Path
from nose.tools import assert_raises, eq_, with_setup
from six.moves import configparser
from termius.core.settings import Config


def clean_tmp_config():
    os.remove(str(Path('/tmp/config')))


@with_setup(teardown=clean_tmp_config)
def test_get_safe_with_nooption():
    config = get_config()
    default = False
    falled_back = config.get_safe('User', 'key', default=default)
    eq_(falled_back, default)


@with_setup(teardown=clean_tmp_config)
def test_get_safe_with_general_error():
    config = get_config()
    with assert_raises(TypeError):
        config.get_safe()


@with_setup(teardown=clean_tmp_config)
def test_get_with_nooption():
    config = get_config()

    with assert_raises(configparser.NoSectionError):
        config.get('User', 'key')


def get_config():
    config = Config(Mock(**{'app.directory_path': '/tmp'}))
    config.touch_files()
    return config
