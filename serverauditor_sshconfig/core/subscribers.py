# -*- coding: utf-8 -*-
import os


def store_ssh_key(sender, command, instance):
    path = instance.file_path(command)
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    with path.open('wb') as _file:
        _file.write(instance.private_key)


def delete_ssh_key(sender, command, instance):
    path = instance.file_path(command)
    if path.is_file():
        os.remove(path)
