# -*- coding: utf-8 -*-
"""Module for Application storage."""
import logging
from collections import namedtuple
from ..signals import (
    pre_create_instance, post_create_instance,
    pre_update_instance, post_update_instance,
    pre_delete_instance, post_delete_instance,
)
from .idgenerators import UUIDGenerator
from .driver import PersistentDict
from ..exceptions import DoesNotExistException, TooManyEntriesException
from .strategies import SaveStrategy, GetStrategy, SoftDeleteStrategy
from .query import Query


# pylint: disable=too-few-public-methods
class InternalModelContructor(object):
    """Serializer raw data from storage to model.

    For internal use only.
    """

    def __init__(self, strategy):
        """Create new constructor."""
        self.strategy = strategy

    def __call__(self, raw_data, model_class):
        """Return barely wrapping raw_data with model_class."""
        return model_class(raw_data)


# pylint: disable=too-few-public-methods
class ModelContructor(InternalModelContructor):
    """Serializer raw data from storage to model."""

    def __call__(self, raw_data, model_class):
        """Call strategy to retrieve complete model tree."""
        model = super(ModelContructor, self).__call__(raw_data, model_class)
        return self.strategy.get(model)


Strategies = namedtuple('Strategies', ('getter', 'saver', 'deleter'))


class ApplicationStorage(object):
    """Storage for user data."""

    path = '{application_directory}/storage'
    defaultstorage = list
    logger = logging.getLogger(__name__)

    def __init__(self, command, save_strategy=None,
                 get_strategy=None, delete_strategy=None, **kwargs):
        """Create new storage for application."""
        paths_kwargs = dict(
            application_directory=command.app.directory_path, **kwargs
        )
        self._path = self.path.format(**paths_kwargs)
        self.driver = PersistentDict(self._path)
        self.id_generator = UUIDGenerator(self)
        self.command = command

        self.strategies = Strategies(
            self.make_strategy(get_strategy, GetStrategy),
            self.make_strategy(save_strategy, SaveStrategy),
            self.make_strategy(delete_strategy, SoftDeleteStrategy)
        )

        self.internal_model_constructor = InternalModelContructor(
            self.strategies.getter)
        self.model_constructor = ModelContructor(
            self.strategies.getter)

    def __enter__(self):
        """Start transaction."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Process transaction closing and sync driver."""
        self.driver.sync()

    def save(self, original_model):
        """Save model to storage.

        Will return model with id and saved mapped fields Model
        instances with ids.
        """
        model = self.strategies.saver.save(original_model)
        if getattr(model, model.id_name):
            saved_model = self.update(model)
        else:
            saved_model = self.create(model)
            original_model.id = model.id

        return saved_model

    def create(self, model):
        """Add new model in it's list."""
        assert not getattr(model, model.id_name)
        pre_create_instance.send(
            model.__class__, command=self.command, instance=model
        )
        model.id = self.generate_id(model)
        updated_model = self._internal_update(model)
        post_create_instance.send(
            model.__class__, command=self.command, instance=model
        )
        return updated_model

    def update(self, model):
        """Update existed model in it's list."""
        identificator = getattr(model, model.id_name)
        assert identificator

        pre_update_instance.send(
            model.__class__, command=self.command, instance=model
        )
        self._internal_delete(model)
        self.strategies.saver.mark_model(model)
        updated_model = self._internal_update(model)
        post_update_instance.send(
            model.__class__, command=self.command, instance=model
        )
        return updated_model

    def delete(self, model):
        """Delete model from it's list."""
        pre_delete_instance.send(
            model.__class__, command=self.command, instance=model
        )
        self._internal_delete(model)
        self.strategies.deleter.delete(model)
        post_delete_instance.send(
            model.__class__, command=self.command, instance=model
        )

    def confirm_delete(self, deleted_sets):
        """Remove intersection with deleted_sets from storage."""
        self.strategies.deleter.remove_intersection(deleted_sets)

    def get(self, model_class, query_union=None, **kwargs):
        """Get single model with passed lookups.

        Usage:
            list = storage.get(Model, any, **{'field.ge': 1, 'field.le': 5}
        """
        founded_models = self.filter(model_class, query_union, **kwargs)
        single_model = self._validate_the_single_model(founded_models)
        return single_model

    def get_single_by_id(self, model_class, identificator):
        """Retrieve single entry by id from storage."""
        assert identificator
        query = Query(all, id=identificator)
        internal_models = self._internal_get_all(model_class)
        founded_models = [i for i in internal_models if query(i)]
        single_model = self._validate_the_single_model(founded_models)
        return self.model_constructor(single_model, model_class)

    def filter(self, model_class, query_union=None, **kwargs):
        """Filter the model list with passed lookups.

        Usage:
            list = storage.filter(Model, any, **{'field.ge': 1, 'field.le': 5}
        """
        assert isinstance(model_class, type)
        assert kwargs
        query = Query(query_union, **kwargs)
        models = self.get_all(model_class)
        founded_models = [i for i in models if query(i)]
        return founded_models

    def exclude(self, model_class, query_union=None, **kwargs):
        """Exclude the model list when matches the lookups.

        Usage:
            list = storage.exclude(Model, any, **{'field.ge': 1, 'field.le': 5}
        """
        assert isinstance(model_class, type)
        assert kwargs
        query = Query(query_union, **kwargs)
        models = self.get_all(model_class)
        founded_models = [i for i in models if not query(i)]
        return founded_models

    def get_all(self, model_class):
        """Retrieve full model list."""
        return self._get_all_base(model_class, self.model_constructor)

    def _internal_get_all(self, model_class):
        return self._get_all_base(model_class, self.internal_model_constructor)

    def _get_all_base(self, model_class, model_contructor):
        assert isinstance(model_class, type)
        name = model_class.set_name
        data = self.driver.setdefault(name, self.defaultstorage())
        models = self.defaultstorage(
            (model_contructor(i, model_class) for i in data)
        )
        return models

    def _internal_update(self, model):
        models = self._internal_get_all(type(model))
        models.append(model)
        self.driver[model.set_name] = models
        return model

    def _internal_delete(self, model):
        identificator = getattr(model, model.id_name)
        assert identificator

        models = self._internal_get_all(type(model))
        for index, model in enumerate(models):
            if model.id == identificator:
                models.pop(index)
                break
        self.driver[model.set_name] = models

    def low_get(self, key):
        """Get data directly from driver."""
        return self.driver[key]

    def low_set(self, key, value):
        """Set data directly to driver."""
        self.driver[key] = value

    def generate_id(self, model):
        """Generate new local id."""
        return self.id_generator(model)

    def make_strategy(self, strategy_class, default):
        """Create new strategy."""
        strategy_class = strategy_class or default
        return strategy_class(self)

    # pylint: disable=no-self-use
    def _validate_the_single_model(self, founded_models):
        if not founded_models:
            raise DoesNotExistException
        elif len(founded_models) != 1:
            raise TooManyEntriesException
        return founded_models[0]
