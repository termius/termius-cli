# -*- coding: utf-8 -*-
"""Module for keeping application config."""
from pathlib2 import Path
from six import PY2
from six.moves import configparser


class Config(object):
    """Class for application config."""

    paths = ['{application_directory}/config']
    write_mode = (PY2 and 'wb') or 'w'

    def __init__(self, command, **kwargs):
        """Create new config."""
        assert self.paths, "It must have at least single config file's path."
        paths_kwargs = dict(
            application_directory=command.app.directory_path, **kwargs
        )
        self._paths = [Path(i.format(**paths_kwargs)) for i in self.paths]
        self.touch_files()
        self.config = configparser.ConfigParser()
        self.config.read([str(i) for i in self._paths])
        self.command = command

    @property
    def ssh_key_dir_path(self):
        """Get path instance to Directory with applications ssh key."""
        try:
            ssh_keys_path = Path(self.config.get('SSH_keys', 'directory'))
        except (configparser.NoSectionError, configparser.NoOptionError):
            ssh_keys_path = self.command.app.directory_path / 'ssh_keys'
            self.set('SSH_keys', 'directory', str(ssh_keys_path))
            self.write()
        return ssh_keys_path

    @property
    def user_config_path(self):
        """Return particular user config path."""
        return self._paths[-1]

    def touch_files(self):
        """Touch config file paths."""
        for i in self._paths:
            if not i.is_file():
                i.touch()

    def get(self, *args, **kwargs):
        """Get option value from config."""
        return self.config.get(*args, **kwargs)

    def get_safe(self, *args, **kwargs):
        """Get option value from config."""
        default = kwargs.pop('default', None)
        try:
            return self.config.get(*args, **kwargs)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

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
        with self.user_config_path.open(self.write_mode) as _file:
            self.config.write(_file)
