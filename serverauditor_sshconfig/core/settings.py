# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import os
try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser


class Config(object):

    paths = ['~/.{application_name}']

    def __init__(self, application_name, **kwargs):
        assert self.paths, "It must have at least single config file's path."
        self._paths = [os.path.expanduser(
            i.format(application_name=application_name, **kwargs)
        ) for i in self.paths]
        self.touch_files()
        self.config = ConfigParser.ConfigParser()
        self.config.read(self._paths)

    @property
    def user_config_path(self):
        return self._paths[-1]

    def touch_files(self):
        for i in self._paths:
            if not os.path.exists(i):
                with open(i, 'w+'):
                    pass

    def get(self, *args, **kwargs):
        self.config.get(*args, **kwargs)

    def set(self, *args, **kwargs):
        self.config.set(*args, **kwargs)

    def close(self):
        with open(self.user_config_path, 'w') as f:
            self.config.write(f)
