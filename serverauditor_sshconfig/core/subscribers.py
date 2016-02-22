# -*- coding: utf-8 -*-
"""Handlers for application signals."""
import six
from .models.terminal import clean_order
from .storage.strategies import SoftDeleteStrategy


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


def clean_data(sender, command, email):
    """Clean data for account with email."""
    with command.storage:
        _clean_data(command.storage)


def _clean_data(storage):
    for model in clean_order:
        instances = storage.get_all(model)
        for i in instances:
            storage.delete(i)

    deleted_set = SoftDeleteStrategy(storage).get_delete_sets()
    storage.confirm_delete(deleted_set)
