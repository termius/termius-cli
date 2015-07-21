# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import os
import six
from uuid import uuid4
from collections import OrderedDict
from .storage import PersistentDict


def expand_and_format_path(paths, **kwargs):
    return [os.path.expanduser(i.format(**kwargs)) for i in paths]


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
        self.config.get(*args, **kwargs)

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


class IDGenerator(object):

    def __init__(self, storage):
        """Contruct IDGenerator.

        :param ApplicationStorage storage: Storage instance
        """

    def __call__(self, model):
        """:param core.models.Model model: generate and set id for this Model."""
        assert not getattr(model, model.id_name)
        uuid = uuid4().int
        setattr(model, model.id_name, uuid)
        return uuid


class ApplicationStorage(object):

    path = '~/.{application_name}.storage'
    defaultstorage = OrderedDict

    def __init__(self, application_name, **kwargs):
        self._path = expand_and_format_path(
            [self.path], application_name=application_name, **kwargs
        )[0]
        self.driver = PersistentDict(self._path)
        self.id_generator = IDGenerator(self)

    def generate_id(self, model):
        return self.id_generator(model)

    def get_all(self, model_class):
        assert isinstance(model_class, type)
        name = model_class.set_name
        dict_data = self.driver.setdefault(name, self.defaultstorage())
        if dict_data:
            model_data = self.defaultstorage(
                ((k, model_class(v)) for k, v in dict_data.items())
            )
        else:
            model_data = dict_data
        return model_data

    def save_mapped_fields(self, model):

        def sub_save(field, mapping):
            submodel = getattr(model, field)
            if not submodel:
                return submodel
            if not mapping.many:
                saved_submodel = self.save(submodel).id
            else:
                saved_submodel = [self.save(submodel).id for i in submodel]

            return saved_submodel

        model_copy = model.copy()
        for field, mapping in model.mapping.items():
            saved_submodel = sub_save(field, mapping)
            setattr(model_copy, field, saved_submodel)
        return model_copy

    def save(self, model):
        """Save model to storage.

        It'll wil call save() for mapped fields, and store only
        it's id or ids (if mapping is many).

        Will return model with id and saved mapped fields Model
        instances with ids.
        """
        if getattr(model, model.id_name):
            self.update(model)
        else:
            self.create(model)
        return model

    def create(self, model):
        assert not getattr(model, model.id_name)
        models = self.get_all(type(model))
        model_with_saved_subs = self.save_mapped_fields(model)
        models[self.generate_id(model)] = model_with_saved_subs
        self.driver[model.set_name] = models
        self.driver.sync()
        return model_with_saved_subs

    def update(self, model):
        identificator = getattr(model, model.id_name)
        assert identificator

        self.save_mapped_fields(model)
        models = self.get_all(type(model))
        model_with_saved_subs = self.save_mapped_fields(model)
        models[identificator] = model_with_saved_subs
        self.driver[model.set_name] = models
        self.driver.sync()

    def get(self, model_class, **kwargs):
        assert isinstance(model_class, type)
        models = self.get_all(model_class)
        identificator = kwargs.get(model_class.id_name)
        return model_class(models[identificator])

    def delete(self, model):
        identificator = getattr(model, model.id_name)
        assert identificator

        models = self[model.set_name]
        models.pop(identificator)
        self.driver[model.set_name] = models
        self.driver.sync()
