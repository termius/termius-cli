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
from .mixins import CryptoChildSerializerCreatorMixin


class BulkSerializer(CryptoChildSerializerCreatorMixin,
                     GetPrimaryKeySerializerMixin,
                     Serializer):
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
        deleted_sets = payload.pop('deleted_sets')
        for set_name, serializer in self.mapping.items():
            models[set_name] = [
                serializer.to_model(i) for i in payload[set_name]
            ]

        deleted_sets_serializer = DeleteSetsSerializer(storage=self.storage)
        models['deleted_sets'] = deleted_sets_serializer.to_model(deleted_sets)
        return models

    def to_payload(self, model):
        """Convert model to payload with set list."""
        payload = {}
        payload['last_synced'] = model.pop('last_synced')
        deleted_sets_serializer = DeleteSetsSerializer(storage=self.storage)
        payload['delete_sets'] = deleted_sets_serializer.to_payload(None)
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


class DeleteSetsSerializer(GetPrimaryKeySerializerMixin,
                           Serializer):
    """Serializer for deleted_sets field."""

    supported_models = (
        SshKey, Snippet,
        SshIdentity, SshConfig,
        Tag, Group,
        Host, PFRule,
        TagHost
    )

    def __init__(self, **kwargs):
        """Construct new serializer for entry list."""
        super(DeleteSetsSerializer, self).__init__(**kwargs)
        self.mapping = OrderedDict((
            (i.set_name, self.get_primary_key_serializer(i))
            for i in self.supported_models
        ))

    def to_model(self, payload):
        """Handle payload to local models and delete them completely."""
        model = {}
        for set_name, serializer in self.mapping.items():
            deleted_set_with_none = [
                self._map_remote_id_to_model(serializer, i)
                for i in payload[set_name]
            ]
            deleted_set = [i for i in deleted_set_with_none if i]
            model[set_name] = deleted_set
            for i in deleted_set:
                self.storage.delete(i)
        self.storage.confirm_delete(payload)
        return model

    def to_payload(self, model):
        """Retrieve local deleted_set."""
        return self.get_delete_strategy().get_delete_sets()

    def soft_delete_entries(self, models):
        """Remove user data and add them to local delete_sets."""
        for i in models:
            self.storage.delete(i)

    def get_delete_strategy(self):
        """Create delete strategy."""
        return SoftDeleteStrategy(self.storage)

    # pylint: disable=no-self-use
    def _map_remote_id_to_model(self, serializer, remote_id):
        try:
            return serializer.to_model(remote_id)
        except DoesNotExistException:
            return None
