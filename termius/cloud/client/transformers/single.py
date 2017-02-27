# -*- coding: utf-8 -*-
"""Module for single entry transformers."""
import logging
from collections import defaultdict
from operator import attrgetter
from ....core.models.base import RemoteInstance
from ....core.exceptions import DoesNotExistException, SkipField
from ....core.models.terminal import (
    SshKey, Identity,
)
from .base import Transformer, DeletBadEncrypted
from .utils import id_getter, map_zip_model_fields


def id_getter_wrapper():
    """Generate id getter."""
    return id_getter


# pylint: disable=abstract-method
class BulkEntryBaseTransformer(Transformer):
    """Base Transformer for one model."""

    def __init__(self, model_class, **kwargs):
        """Create new entry transformer."""
        super(BulkEntryBaseTransformer, self).__init__(**kwargs)
        assert model_class
        self.model_class = model_class
        self.sync_keys = (
            self.account_manager.get_settings()['synchronize_key']
        )
        self.skip = (
            not self.sync_keys and
            self.model_class in (SshKey, Identity)
        )


class BulkPrimaryKeyTransformer(BulkEntryBaseTransformer):
    """Transformer for primary key payloads."""

    logger = logging.getLogger(__name__)
    to_model_mapping = defaultdict(id_getter_wrapper, {int: int, })

    def to_model(self, payload):
        """Retrieve model from storage by payload."""
        if not payload:
            return None
        if self.skip:
            raise SkipField

        remote_instance_id = self.id_from_payload(payload)
        model = self.storage.get(
            self.model_class,
            **{'remote_instance.id': remote_instance_id}
        )
        return model

    def to_payload(self, model):
        """Convert model to primary key or to set/id reference."""
        if self.skip:
            raise SkipField
        if not model:
            return None
        if model.remote_instance:
            return model.remote_instance.id
        else:
            return '{model.set_name}/{model.id}'.format(model=model)

    def id_from_payload(self, payload):
        """Get remote id from payload."""
        return self.to_model_mapping[type(payload)](payload)


# pylint: disable=too-few-public-methods
class GetPrimaryKeyTransformerMixin(object):
    """Mixin to get primary get Transformer."""

    def get_primary_key_transformer(self, model_class):
        """Create new primary key Transformer."""
        return BulkPrimaryKeyTransformer(
            storage=self.storage, model_class=model_class,
            account_manager=self.account_manager,
        )


class BulkEntryTransformer(GetPrimaryKeyTransformerMixin,
                           BulkPrimaryKeyTransformer):
    """Transformer for complete model."""

    def __init__(self, **kwargs):
        """Create new Transformer."""
        super(BulkEntryTransformer, self).__init__(**kwargs)
        self.attrgetter = attrgetter(*self.model_class.fields)
        self.remote_instance_attrgetter = attrgetter(*RemoteInstance.fields)

    def to_payload(self, model):
        """Convert model to payload."""
        if self.skip:
            raise SkipField
        payload = dict(map_zip_model_fields(model, self.attrgetter))
        if model.remote_instance:
            zipped_remote_instance = map_zip_model_fields(
                model.remote_instance, self.remote_instance_attrgetter
            )
            payload.update(zipped_remote_instance)

        for field, mapping in model.fields.items():
            self.serialize_field(payload, model, field, mapping)
        payload['local_id'] = model.id
        return payload

    def serialize_field(self, payload, model, field, mapping):
        """Transform field to payload or skip."""
        try:
            if field in model.fk_field_names():
                payload[field] = self.serialize_related_field(
                    model, field, mapping
                )
            else:
                payload[field] = getattr(model, field)
        except SkipField:
            payload.pop(field, None)

    def serialize_related_field(self, model, field, mapping):
        """Transform relation to payload."""
        related_transformer = self.get_primary_key_transformer(mapping.model)
        fk_payload = related_transformer.to_payload(getattr(model, field))
        return fk_payload

    def to_model(self, payload):
        """Convert payload to model."""
        if self.skip:
            raise SkipField

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
        for i, mapping in model.fields.items():
            if i in fk_fields:
                try:
                    models_fields[i] = self.render_relation_field(
                        mapping, payload[i]
                    )
                except SkipField:
                    models_fields.pop(i, None)
        model.update(models_fields)
        model.remote_instance = self.create_remote_instance(payload)
        return model

    def get_or_initialize_model(self, payload):
        """Get existed model or generate new one using payload."""
        try:
            model = self.get_model(payload)
        except DoesNotExistException:
            model = self.initialize_model()

        model.id = payload.get('local_id', model.id)
        return model

    def get_model(self, payload):
        """Get model for payload."""
        return super(BulkEntryTransformer, self).to_model(payload)

    def render_relation_field(self, mapping, value):
        """Convert relation mapping and value to whole model."""
        transformer = self.get_primary_key_transformer(mapping.model)
        return transformer.to_model(value)

    def initialize_model(self):
        """Generate new model using payload."""
        model = self.model_class()
        return model

    # pylint: disable=no-self-use
    def create_remote_instance(self, payload):
        """Generate remote instance for payload."""
        instance = RemoteInstance()
        instance.init_from_payload(payload)
        return instance


class CryptoBulkEntryTransformer(BulkEntryTransformer):
    """Entry Transformer that encrypt model and decrypt payload."""

    def __init__(self, crypto_controller, **kwargs):
        """Construct new crypto Transformer for bulk entry."""
        super(CryptoBulkEntryTransformer, self).__init__(**kwargs)
        self.crypto_controller = crypto_controller

    def to_model(self, payload):
        """Decrypt model after serialization."""
        model = super(CryptoBulkEntryTransformer, self).to_model(payload)
        try:
            descrypted_model = self.crypto_controller.decrypt(model)
        except self.crypto_controller.bad_encrypted_exception:
            raise DeletBadEncrypted(model)
        return self.storage.save(descrypted_model)

    def to_payload(self, model):
        """Encrypt model before deserialization."""
        encrypted_model = self.crypto_controller.encrypt(model)
        return super(CryptoBulkEntryTransformer, self).to_payload(
            encrypted_model
        )


class SettingsTransformer(Transformer):
    """Transformer for settings."""

    def to_model(self, payload):
        """Convert REST API payload to Application models."""
        return payload

    def to_payload(self, model):
        """Convert Application models to REST API payload."""
        return model
