# -*- coding: utf-8 -*-
from collections import defaultdict
from operator import attrgetter
from ....core.models import RemoteInstance
from ....core.exceptions import DoesNotExistException
from .base import Serializer
from .utils import id_getter, map_zip_model_fields


def id_getter_wrapper():
    return id_getter


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

    to_model_mapping = defaultdict(id_getter_wrapper, {int: int, })

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
            if field in model.fk_field_names():
                payload[field] = self.serialize_related_field(
                    model, field, mapping
                )
            else:
                payload[field] = getattr(model, field)
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
        models_fields = {
            i: payload[i]
            for i, mapping in model.fields.items()
            if i not in fk_fields
        }
        models_fields.update([
            (i, self.render_relation_field(mapping, payload[i]))
            for i, mapping in model.fields.items()
            if i in fk_fields
        ])
        model.update(models_fields)
        model.remote_instance = self.create_remote_instance(payload)
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

    def render_relation_field(self, mapping, value):
        serializer = self.get_primary_key_serializer(mapping.model)
        return serializer.to_model(value)

    def initialize_model(self, payload):
        """Generate new model using payload."""
        model = self.model_class()
        return model

    # pylint: disable=no-self-use
    def create_remote_instance(self, payload):
        """Generate remote instance for payload."""
        instance = RemoteInstance()
        instance.init_from_payload(payload)
        return instance


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
