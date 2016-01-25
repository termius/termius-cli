import copy
from collections import namedtuple


Field = namedtuple('Field', ('model', 'many', 'default'))


class AbstractModel(dict):

    fields = dict()
    _mandatory_fields = dict()

    @classmethod
    def _fields(cls):
        copy_fields = cls.fields.copy()
        copy_mandatory_fields = cls._mandatory_fields.copy()
        copy_fields.update(copy_mandatory_fields)
        return copy_fields

    @classmethod
    def allowed_fields(cls):
        return cls._fields().keys()

    @classmethod
    def _validate_attr(cls, name):
        if name not in cls.allowed_fields():
            raise AttributeError

    def __getattr__(self, name):
        self._validate_attr(name)
        default = self._fields()[name].default
        return self.get(name, default)

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
        return type(self)(copy.deepcopy(super(AbstractModel, self)))


class RemoteInstance(AbstractModel):

    fields = {
        'id': Field(long, False, None),
        'updated': Field(bool, False, False),
        'updated_at': Field(str, False, None),
    }


class Model(AbstractModel):

    _mandatory_fields = {
        'id': Field(long, False, None),
        'remote_instance': Field(RemoteInstance, False, None)
    }

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        is_need_to_patch_remote_instance = (
            self.remote_instance and
            not isinstance(self.remote_instance, RemoteInstance)
        )
        if is_need_to_patch_remote_instance:
            self.remote_instance = RemoteInstance(self.remote_instance)

    @classmethod
    def fk_field_names(cls):
        return tuple(
            k for k, v in cls._fields().items() if issubclass(v.model, Model)
        )

    def mark_updated(self):
        if self.remote_instance:
            self.remote_instance.updated = True

    # set_name = ''
    # """Key name in Application Storage."""
    crypto_fields = {}
    """Set of fields for enrpyption and decryption on cloud."""

    id_name = 'id'
    """Name of field to be used as identificator."""


class DeleteSets(AbstractModel):

    fields = {
        'tag_set': Field(list, False, None),
        'snippet_set': Field(list, False, None),
        'sshkeycrypt_set': Field(list, False, None),
        'sshidentity_set': Field(list, False, None),
        'sshconfig_set': Field(list, False, None),
        'group_set': Field(list, False, None),
        'host_set': Field(list, False, None),
        'taghost_set': Field(list, False, None),
        'pfrule_set': Field(list, False, None),
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
