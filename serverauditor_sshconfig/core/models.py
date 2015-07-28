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


class DeleteSets(AbstractModel):

    fields = {
        'tag_set', 'snippet_set', 'sshkeycrypt_set', 'sshidentity_set',
        'sshconfig_set', 'group_set', 'host_set', 'taghost_set',
        'pfrule_set',

    }
    set_name = 'delete_sets'
    default_field_value = list

    def update_field(self, field, set_operator):
        existed = getattr(self, field) or self.default_field_value()
        existed_set = set(existed)
        new_set = set_operator(existed_set)
        new = self.default_field_value(new_set)
        setattr(self, model.set_name, new)

    def soft_delete(self, model):
        if not model.remote_instance:
            return

        def union(existed_set):
            return existed_set.union({model.remote_instance.id})

        self.update_field(model.set_name, union)

    def delete_soft_deleted(self, set_name, identity):
        if not identity:
            return

        def intersection(existed_set):
            return existed_set.intersection({identity})

        self.update_field(set_name, intersection)
