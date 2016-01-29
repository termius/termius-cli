# -*- coding: utf-8 -*-
"""Module with many then 1 entry transformers."""
from collections import OrderedDict
from ....core.exceptions import DoesNotExistException
from ....core.storage.strategies import SoftDeleteStrategy
from ...models import (
    Host, Group,
    Tag, SshKey,
    SshIdentity, SshConfig,
    PFRule, TagHost,
    Snippet,
)
from .base import Serializer
from .single import GetPrimaryKeySerializerMixin, CryptoBulkEntrySerializer


class BulkSerializer(GetPrimaryKeySerializerMixin, Serializer):
    """Serializer for entry list."""

    child_serializer_class = CryptoBulkEntrySerializer
    supported_models = (
        SshKey, Snippet,
        SshIdentity, SshConfig,
        Tag, Group,
        Host, PFRule,
        TagHost
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
        self.storage.confirm_delete(deleted_sets)
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
                    'remote_instance.state.rcontains': ['created', 'updated'],
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
