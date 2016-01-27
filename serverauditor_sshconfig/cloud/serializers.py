# -*- coding: utf-8 -*-
"""Serializers (read controllers) is like django rest framework serializers."""
import abc
from collections import OrderedDict, defaultdict
from operator import attrgetter, itemgetter
import six
from ..core.models import RemoteInstance
from ..core.exceptions import DoesNotExistException
from ..core.storage.strategies import SoftDeleteStrategy
from .models import (
    Host, Group,
    Tag, SshKey,
    SshIdentity, SshConfig,
    PFRule, TagHost,
)

ID_GETTER = itemgetter('id')


def map_zip_model_fields(model, field_getter=None):
    """Return list of tuples (field_object, field_value)."""
    field_getter = field_getter or attrgetter(model.fields)
    return zip(model.fields, field_getter(model))


@six.add_metaclass(abc.ABCMeta)
class Serializer(object):
    """Base serializer."""

    def __init__(self, storage):
        """Create new Serializer."""
        assert storage
        self.storage = storage

    @abc.abstractmethod
    def to_model(self, payload):
        """Convert REST API payload to Application models."""

    @abc.abstractmethod
    def to_payload(self, model):
        """Convert Application models to REST API payload."""
        pass


# pylint: disable=abstract-method
class BulkEntryBaseSerializer(Serializer):
    """Base serializer for one model."""

    def __init__(self, model_class, **kwargs):
        """Create new entry serializer."""
        super(BulkEntryBaseSerializer, self).__init__(**kwargs)
        assert model_class
        self.model_class = model_class


class BulkPrimaryKeySerializer(BulkEntryBaseSerializer):
    """Serializer for primary key payloads."""

    to_model_mapping = defaultdict(
        lambda: ID_GETTER, {int: int, }
    )

    def id_from_payload(self, payload):
        """Get remote id from payload."""
        return self.to_model_mapping[type(payload)](payload)

    def to_model(self, payload):
        """Retrieve model from storage by payload."""
        if not payload:
            return None

        remote_instance_id = self.id_from_payload(payload)
        model = self.storage.get(
            self.model_class,
            **{'remote_instance.id': remote_instance_id}
        )
        return model

    def to_payload(self, model):
        """Convert model to primary key or to set/id reference."""
        if not model:
            return None
        if model.remote_instance:
            return model.remote_instance.id
        else:
            return '{model.set_name}/{model.id}'.format(model=model)


# pylint: disable=too-few-public-methods
class GetPrimaryKeySerializerMixin(object):
    """Mixin to get primary get serializer."""

    def get_primary_key_serializer(self, model_class):
        """Create new primary key serializer."""
        return BulkPrimaryKeySerializer(
            storage=self.storage, model_class=model_class
        )


class BulkEntrySerializer(GetPrimaryKeySerializerMixin,
                          BulkPrimaryKeySerializer):
    """Serializer for complete model."""

    def __init__(self, **kwargs):
        """Create new serializer."""
        super(BulkEntrySerializer, self).__init__(**kwargs)
        self.attrgetter = attrgetter(*self.model_class.fields)
        self.remote_instance_attrgetter = attrgetter(*RemoteInstance.fields)

    def to_payload(self, model):
        """Convert model to payload."""
        payload = dict(map_zip_model_fields(model, self.attrgetter))
        if model.remote_instance:
            zipped_remote_instance = map_zip_model_fields(
                model.remote_instance, self.remote_instance_attrgetter
            )
            payload.update(zipped_remote_instance)
        for field, mapping in model.fields.items():
            payload[field] = self.serialize_related_field(
                model, field, mapping
            )
        payload['local_id'] = model.id
        return payload

    def serialize_related_field(self, model, field, mapping):
        """Serializer relation to payload."""
        related_serializer = self.get_primary_key_serializer(mapping.model)
        fk_payload = related_serializer.to_payload(getattr(model, field))
        return fk_payload

    def to_model(self, payload):
        """Convert payload to model."""
        model = self.get_or_initialize_model(payload)
        model = self.update_model_fields(model, payload)
        return model

    def update_model_fields(self, model, payload):
        """Update model's fields with payload."""
        fk_fields = model.fk_field_names()
        for i in model.fields:
            if i in fk_fields:
                mapping = model.fields.get(i)
                serializer = self.get_primary_key_serializer(mapping.model)
                field = serializer.to_model(payload[i])
            else:
                field = payload[i]
            setattr(model, i, field)
        return model

    def get_or_initialize_model(self, payload):
        """Get existed model or generate new one using payload."""
        try:
            model = self.get_model(payload)
        except DoesNotExistException:
            model = self.initialize_model(payload)

        model.id = payload.get('local_id', model.id)
        return model

    def get_model(self, payload):
        """Get model for payload."""
        return super(BulkEntrySerializer, self).to_model(payload)

    def initialize_model(self, payload):
        """Generate new model using payload."""
        remote_instance = self.create_remote_instance(payload)
        model = self.model_class()
        model.remote_instance = remote_instance
        model.update(
            ((k, v) for k, v in payload.items() if k in model.fields)
        )
        return model

    # pylint: disable=no-self-use
    def create_remote_instance(self, payload):
        """Generate remote instance for payload."""
        remote_instance = RemoteInstance()
        for i, field in RemoteInstance.fields.items():
            setattr(remote_instance, i, payload.pop(i, field.default))
        return remote_instance


class CryptoBulkEntrySerializer(BulkEntrySerializer):
    """Entry serializer that encrypt model and decrypt payload."""

    def __init__(self, crypto_controller, **kwargs):
        """Construct new crypto serializer for bulk entry."""
        super(CryptoBulkEntrySerializer, self).__init__(**kwargs)
        self.crypto_controller = crypto_controller

    def to_model(self, payload):
        """Decrypt model after serialization."""
        model = super(CryptoBulkEntrySerializer, self).to_model(payload)
        return self.crypto_controller.decrypt(model)

    def to_payload(self, model):
        """Encrypt model before deserialization."""
        encrypted_model = self.crypto_controller.encrypt(model)
        return super(CryptoBulkEntrySerializer, self).to_payload(
            encrypted_model)


class BulkSerializer(GetPrimaryKeySerializerMixin, Serializer):
    """Serializer for entry list."""

    child_serializer_class = CryptoBulkEntrySerializer
    supported_models = (
        SshKey, SshIdentity, SshConfig, Tag, Group, Host, PFRule, TagHost
    )

    def __init__(self, crypto_controller, **kwargs):
        """Construct new serializer for entry list."""
        super(BulkSerializer, self).__init__(**kwargs)
        self.crypto_controller = crypto_controller
        self.mapping = OrderedDict((
            (i.set_name, self.create_child_serializer(i))
            for i in self.supported_models
        ))

    def to_model(self, payload):
        """Convert payload with set list."""
        models = {}
        models['last_synced'] = payload.pop('now')
        models['deleted_sets'] = {}
        deleted_sets = payload.pop('deleted_sets')
        for set_name, serializer in self.mapping.items():
            models[set_name] = [
                serializer.to_model(i) for i in payload[set_name]
            ]
            serializer = self.get_primary_key_serializer(
                serializer.model_class
            )
            deleted_set = []
            for i in deleted_sets[set_name]:
                try:
                    deleted_set.append(serializer.to_model(i))
                except DoesNotExistException:
                    continue
            models['deleted_sets'][set_name] = deleted_set

            self.process_model_entries(
                models[set_name], models['deleted_sets'][set_name]
            )
        self.storage.confirm_delete(models['deleted_sets'])
        return models

    def to_payload(self, model):
        """Convert model to payload with set list."""
        payload = {}
        payload['last_synced'] = model.pop('last_synced')
        payload['delete_sets'] = self.get_delete_strategy().get_delete_sets()
        for set_name, serializer in self.mapping.items():
            internal_model = self.storage.filter(
                serializer.model_class, any,
                **{
                    'remote_instance.updated': True,
                    'remote_instance': None
                }
            )
            payload[set_name] = [
                serializer.to_payload(i) for i in internal_model
            ]
        return payload

    def get_delete_strategy(self):
        """Create delete strategy."""
        return SoftDeleteStrategy(self.storage)

    def create_child_serializer(self, model_class):
        """Generate specific set serializer."""
        return self.child_serializer_class(
            model_class=model_class, storage=self.storage,
            crypto_controller=self.crypto_controller
        )

    def process_model_entries(self, updated, deleted):
        """Handle updated and deleted models."""
        for i in updated:
            self.storage.save(i)
        for i in deleted:
            self.storage.delete(i)
