# -*- coding: utf-8 -*-
"""Module with general model implementation."""
import copy
from collections import namedtuple


Field = namedtuple('Field', ('model', 'many', 'default'))


class AbstractModel(dict):
    """Base class for all models."""

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
        """Return list of fields for application usage."""
        return cls._fields().keys()

    def __getattr__(self, name):
        """Get field from self."""
        return self.get(name, None)

    def __setattr__(self, name, value):
        """Set field to self."""
        self[name] = value

    def __delattr__(self, name):
        """Delete key from self."""
        del self[name]

    def copy(self):
        """Wrap dict.copy into model."""
        return self.__copy__()

    def __copy__(self):
        """Wrap dict.copy into model."""
        newone = type(self)()
        newone.update(self)
        return newone

    # pylint: disable=unused-argument
    def __deepcopy__(self, requesteddeepcopy):
        """Wrap dict.deepcopy into model."""
        return type(self)(copy.deepcopy(dict(self)))


class RemoteInstance(AbstractModel):
    """Class that represent model sync revision."""

    fields = {
        'id': Field(int, False, None),
        # States could be one of 'created' / 'updated' / 'synced'
        'state': Field(str, False, 'synced'),
        'updated_at': Field(str, False, None),
    }

    def init_from_payload(self, response_payload):
        """Update remote instance field with response payload ones."""
        for i, field in self.fields.items():
            setattr(self, i, response_payload.pop(i, field.default))


class Model(AbstractModel):
    """Base model with relations."""

    _mandatory_fields = {
        'id': Field(int, False, None),
        'remote_instance': Field(RemoteInstance, False, None)
    }

    def __init__(self, *args, **kwargs):
        """Create new model and patch remote instance."""
        # The simplest way to make lint not raise
        #   access-member-before-definition
        self.remote_instance = None
        super(Model, self).__init__(*args, **kwargs)
        is_need_to_patch_remote = (
            self.remote_instance and
            not isinstance(self.remote_instance, RemoteInstance)
        )
        if is_need_to_patch_remote:
            self.remote_instance = RemoteInstance(self.remote_instance)

    @classmethod
    def fk_field_names(cls):
        """Return name list for relation fields."""
        return tuple(
            k for k, v in cls._fields().items() if issubclass(v.model, Model)
        )

    def mark_updated(self):
        """Mark revision as outdated."""
        if self.remote_instance:
            # pylint: disable=attribute-defined-outside-init
            self.remote_instance.state = 'updated'

    def mark_synced(self):
        """Mark revision as updated."""
        if self.remote_instance:
            # pylint: disable=attribute-defined-outside-init
            self.remote_instance.state = 'synced'

    # set_name = ''
    # """Key name in Application Storage."""
    crypto_fields = {}
    """Set of fields for encryption and decryption on cloud."""

    id_name = 'id'
    """Name of field to be used as identificator."""


class DeleteSets(AbstractModel):
    """Class to keep deleted model remote references."""

    fields = {
        'tag_set': Field(list, False, None),
        'snippet_set': Field(list, False, None),
        'sshkeycrypt_set': Field(list, False, None),
        'identity_set': Field(list, False, None),
        'sshconfig_set': Field(list, False, None),
        'group_set': Field(list, False, None),
        'host_set': Field(list, False, None),
        'taghost_set': Field(list, False, None),
        'pfrule_set': Field(list, False, None),
        'knownhost_set': Field(list, False, None),
        'telnetconfig_set': Field(list, False, None)
    }
    set_name = 'delete_sets'
    default_field_value = list

    def update_field(self, field, set_operator):
        """Update the one of deleted_set."""
        existed = getattr(self, field) or self.default_field_value()
        existed_set = set(existed)
        new_set = set_operator(existed_set)
        new = self.default_field_value(new_set)
        setattr(self, field, new)

    def store(self, model):
        """Add model id to deleted_sets."""
        if not model.remote_instance:
            return

        def union(existed_set):
            return existed_set.union({model.remote_instance.id})

        self.update_field(model.set_name, union)

    def remove_all(self, set_name, identities):
        """Remove id from deleted_sets."""
        if not identities:
            return

        def intersection(existed_set):
            return existed_set - set(identities)

        self.update_field(set_name, intersection)
