import copy
from collections import namedtuple


Mapping = namedtuple('Mapping', ('model', 'many'))


class AbstractModel(dict):

    fields = set()
    _mandatory_fields = set()

    @classmethod
    def allowed_feilds(cls):
        return tuple(cls.fields.union(cls._mandatory_fields))

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
        newone.update(self)
        return newone

    def __deepcopy__(self, requesteddeepcopy):
        return type(self)(copy.deepcopy(super(Model, self)))


class Model(AbstractModel):

    _mandatory_fields = {'id', 'remote_instance'}

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        is_need_to_patch_remote_instance = (
            self.remote_instance and
            not isinstance(self.remote_instance, RemoteInstance)
        )
        if is_need_to_patch_remote_instance:
            self.remote_instance = RemoteInstance(self.remote_instance)

    # set_name = ''
    # """Key name in Application Storage."""
    mapping = {}
    """Foreign key mapping - Mapping instances per field_name."""
    crypto_fields = {}
    """Set of fields for enrpyption and decryption on cloud."""

    id_name = 'id'
    """Name of field to be used as identificator."""


class RemoteInstance(AbstractModel):

    fields = {'id', 'updated_at'}
