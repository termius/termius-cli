from .idgenerators import UUIDGenerator
from .driver import PersistentDict
from ..utils import expand_and_format_path, tupled_attrgetter
from ..exceptions import DoesNotExistException, TooManyEntriesException
from .strategies import SaveStrategy, GetStrategy


class InternalModelContructor(object):

    def __init__(self, strategy):
        self.strategy = strategy

    def __call__(self, raw_data, model_class):
        return model_class(raw_data)


class ModelContructor(InternalModelContructor):

    def __call__(self, raw_data, model_class):
        model = super(ModelContructor, self).__call__(raw_data, model_class)
        return self.strategy.get(model)


class ApplicationStorage(object):

    path = '~/.{application_name}.storage'
    defaultstorage = list

    def __init__(self, application_name, save_strategy=None, get_strategy=None, **kwargs):
        self._path = expand_and_format_path(
            [self.path], application_name=application_name, **kwargs
        )[0]
        self.driver = PersistentDict(self._path)
        self.id_generator = UUIDGenerator(self)

        save_strategy_class = save_strategy or SaveStrategy
        self.save_strategy = save_strategy_class(self)
        get_strategy_class = get_strategy or GetStrategy
        self.get_strategy = get_strategy_class(self)

        self.internal_model_constructor = InternalModelContructor(
            self.get_strategy)
        self.model_constructor = ModelContructor(
            self.get_strategy)

    def generate_id(self, model):
        return self.id_generator(model)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.sync()

    def save(self, model):
        """Save model to storage.

        It'll wil call save() for mapped fields, and store only
        it's id or ids (if mapping is many).

        Will return model with id and saved mapped fields Model
        instances with ids.
        """
        model = self.save_strategy.save(model)
        if getattr(model, model.id_name):
            saved_model = self.update(model)
        else:
            saved_model = self.create(model)
        return saved_model

    def create(self, model):
        assert not getattr(model, model.id_name)
        model.id = self.generate_id(model)
        models = self._internal_get_all(type(model))
        models.append(model)
        self.driver[model.set_name] = models
        return model

    def update(self, model):
        identificator = getattr(model, model.id_name)
        assert identificator

        self.delete(model)
        models = self._internal_get_all(type(model))
        models.append(model)
        self.driver[model.set_name] = models
        return model

    def get(self, model_class, query_union=None, **kwargs):
        founded_models = self.filter(model_class, query_union, **kwargs)
        if not founded_models:
            raise DoesNotExistException
        elif len(founded_models) != 1:
            raise TooManyEntriesException
        return founded_models[0]

    def filter(self, model_class, query_union=None, **kwargs):
        assert isinstance(model_class, type)
        assert kwargs
        query_operator = query_union or all
        models = self.get_all(model_class)
        filter_keys = tuple(i[0] for i in kwargs.items())
        filter_values = tuple(i[1] for i in kwargs.items())
        getter = tupled_attrgetter(*filter_keys)

        def perform_query(got):
            fields_values_equal = (
                attribute == value for attribute, value
                in zip(getter(got), filter_values)
            )
            return query_operator(fields_values_equal)

        founded_models = [i for i in models if perform_query(i)]
        return founded_models

    def _get_all_base(self, model_class, model_contructor):
        assert isinstance(model_class, type)
        name = model_class.set_name
        data = self.driver.setdefault(name, self.defaultstorage())
        models = self.defaultstorage(
            (model_contructor(i, model_class) for i in data)
        )
        return models

    def _internal_get_all(self, model_class):
        return self._get_all_base(model_class, self.internal_model_constructor)

    def get_all(self, model_class):
        return self._get_all_base(model_class, self.model_constructor)

    def delete(self, model):
        identificator = getattr(model, model.id_name)
        assert identificator

        models = self._internal_get_all(type(model))
        for index, model in enumerate(models):
            if model.id == identificator:
                models.pop(index)
                break
        self.driver[model.set_name] = models
