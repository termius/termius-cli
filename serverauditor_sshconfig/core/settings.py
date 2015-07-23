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
from .exceptions import DoesNotExistException


def expand_and_format_path(paths, **kwargs):
    return [os.path.expanduser(i.format(**kwargs)) for i in paths]


def tupled_attrgetter(*items):
    def g(obj):
        return tuple(resolve_attr(obj, attr) for attr in items)
    return g


def resolve_attr(obj, attr):
    for name in attr.split("."):
        obj = getattr(obj, name)
    return obj


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


class IDGenerator(object):

    def __init__(self, storage):
        """Contruct IDGenerator.

        :param ApplicationStorage storage: Storage instance
        """

    def __call__(self, model):
        """:param core.models.Model model: generate and set id for this Model."""
        assert not getattr(model, model.id_name)
        identificator = uuid4().time_low
        setattr(model, model.id_name, identificator)
        return identificator


class ApplicationStorage(object):

    path = '~/.{application_name}.storage'
    defaultstorage = list

    def __init__(self, application_name, **kwargs):
        self._path = expand_and_format_path(
            [self.path], application_name=application_name, **kwargs
        )[0]
        self.driver = PersistentDict(self._path)
        self.id_generator = IDGenerator(self)

    def generate_id(self, model):
        return self.id_generator(model)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.sync()

    def save_mapped_fields(self, model):

        def save_instance(model):
            if isinstance(model, six.integer_types):
                return model
            return self.save(model).id

        def sub_save(field, mapping):
            submodel = getattr(model, field)
            if not mapping.many:

                saved_submodel = submodel and save_instance(submodel)
            else:
                submodel = submodel or []
                saved_submodel = [save_instance(i) for i in submodel]
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
        model_with_saved_subs = self.save_mapped_fields(model)
        model.id = self.generate_id(model_with_saved_subs)
        models = self.get_all(type(model))
        models.append(model_with_saved_subs)
        self.driver[model.set_name] = models
        return model_with_saved_subs

    def update(self, model):
        identificator = getattr(model, model.id_name)
        assert identificator

        self.save_mapped_fields(model)
        model_with_saved_subs = self.save_mapped_fields(model)

        self.delete(model)
        models = self.get_all(type(model))
        models.append(model_with_saved_subs)
        self.driver[model.set_name] = models

    def get(self, model_class, **kwargs):
        assert isinstance(model_class, type)
        assert kwargs
        models = self.get_all(model_class)
        filter_keys = tuple(i[0] for i in kwargs.items())
        filter_values = tuple(i[1] for i in kwargs.items())
        getter = tupled_attrgetter(*filter_keys)
        founded_models = [
            i for i in models if getter(i) == filter_values
        ]
        if not founded_models:
            raise DoesNotExistException
        assert len(founded_models) == 1
        return model_class(founded_models[0])

    def get_all(self, model_class):
        assert isinstance(model_class, type)
        name = model_class.set_name
        data = self.driver.setdefault(name, self.defaultstorage())
        models = self.defaultstorage(
            (model_class(i) for i in data)
        )
        return models

    def delete(self, model):
        identificator = getattr(model, model.id_name)
        assert identificator

        models = self.get_all(type(model))
        for index, model in enumerate(models):
            if model.id == identificator:
                models.pop(index)
                break
        self.driver[model.set_name] = models
