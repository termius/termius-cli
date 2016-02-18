# -*- coding: utf-8 -*-
"""Handlers for application signals."""
import six


# pylint: disable=unused-argument
def store_ssh_key(sender, command, instance):
    """Write private key to file."""
    if not instance.private_key:
        return
    path = instance.file_path(command)
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    path.write_text(six.text_type(instance.private_key))
    path.chmod(instance.file_mode)


# pylint: disable=unused-argument
def delete_ssh_key(sender, command, instance):
    """Delete private key file."""
    path = instance.file_path(command)
    if path.is_file():
        path.unlink()
