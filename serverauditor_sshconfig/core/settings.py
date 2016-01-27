# -*- coding: utf-8 -*-
"""Module for keeping application config."""
import os
import six
from .utils import expand_and_format_path


class Config(object):
    """Class for application config."""

    paths = ['~/.{application_name}']

    def __init__(self, application_name, **kwargs):
        """Create new config."""
        assert self.paths, "It must have at least single config file's path."
        self._paths = expand_and_format_path(
            self.paths, application_name=application_name, **kwargs
        )
        self.touch_files()
        self.config = six.moves.configparser.ConfigParser()
        self.config.read(self._paths)

    @property
    def user_config_path(self):
        """Return particular user config path."""
        return self._paths[-1]

    def touch_files(self):
        """Touch config file paths."""
        for i in self._paths:
            if not os.path.exists(i):
                with open(i, 'w+'):
                    pass

    def get(self, *args, **kwargs):
        """Get option value from config."""
        return self.config.get(*args, **kwargs)

    def set(self, section, option, value):
        """Set option value to config."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def remove(self, section, option):
        """Remove option value from config."""
        if self.config.has_section(section):
            self.config.remove_option(section, option)

    def remove_section(self, section):
        """Remove section and all options from config."""
        if self.config.has_section(section):
            self.config.remove_section(section)

    def write(self):
        """Write config for current user config file."""
        with open(self.user_config_path, 'w') as _file:
            self.config.write(_file)
