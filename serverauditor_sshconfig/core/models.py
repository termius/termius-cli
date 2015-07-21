import six
import abc
import copy
from collections import namedtuple


Mapping = namedtuple('Mapping', ('model', 'many'))


class Model(dict):

    fields = set()

    __mandatory_fields = {'id', 'remote_instance'}

    @classmethod
    def allowed_feilds(cls):
        return tuple(cls.fields.union(cls.__mandatory_fields))

    @classmethod
    def _validate_attr(cls, name):
        if name not in cls.allowed_feilds():
            raise AttributeError

    def __getattr__(self, name):
        self._validate_attr(name)
        return self.get(name)

    def __setattr__(self, name, value):
        self._validate_attr(name)
        self[name] = value

    def __delattr__(self, name):
        self._validate_attr(name)
        del self[name]

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone

    def __deepcopy__(self, requesteddeepcopy):
        return type(self)(copy.deepcopy(super(Model, self)))

    # set_name = ''
    # """Key name in Application Storage."""
    # mapping = {}
    # """Foreign key mapping - Mapping instances per field_name."""

    id_name = 'id'
    """Name of field to be used as identificator."""


class RemoteInstance(Model):

    fields = {'id', 'updated_at'}
