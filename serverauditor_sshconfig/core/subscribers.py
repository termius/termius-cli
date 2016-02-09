# -*- coding: utf-8 -*-
"""Handlers for application signals."""
import os


# pylint: disable=unused-argument
def store_ssh_key(sender, command, instance):
    """Write private key to file."""
    path = instance.file_path(command)
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    with path.open('wb') as _file:
        _file.write(instance.private_key)


# pylint: disable=unused-argument
def delete_ssh_key(sender, command, instance):
    """Delete private key file."""
    path = instance.file_path(command)
    if path.is_file():
        os.remove(str(path))
