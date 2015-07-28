# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import os
import six
from .utils import expand_and_format_path


class Config(object):

    paths = ['~/.{application_name}']

    def __init__(self, application_name, **kwargs):
        assert self.paths, "It must have at least single config file's path."
        self._paths = expand_and_format_path(
            self.paths, application_name=application_name, **kwargs
        )
        self.touch_files()
        self.config = six.moves.configparser.ConfigParser()
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
        return self.config.get(*args, **kwargs)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def remove(self, section, option):
        if self.config.has_section(section):
            self.config.remove_option(section, option)

    def remove_section(self, section):
        if self.config.has_section(section):
            self.config.remove_section(section)

    def write(self):
        with open(self.user_config_path, 'w') as f:
            self.config.write(f)
