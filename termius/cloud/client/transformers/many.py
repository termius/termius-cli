# -*- coding: utf-8 -*-
"""Module with many then 1 entry transformers."""
from collections import OrderedDict
from ....core.exceptions import DoesNotExistException, SkipField
from ....core.storage.strategies import SoftDeleteStrategy
from ....core.models.terminal import (
    Host, Group,
    Tag, SshKey,
    Identity, SshConfig,
    PFRule, TagHost,
    Snippet
)
from .base import Transformer
from .single import GetPrimaryKeyTransformerMixin, CryptoBulkEntryTransformer
from .mixins import CryptoChildTransformerCreatorMixin


# pylint: disable=abstract-method
class ManyTransformer(Transformer):
    """Base class for all many transformers."""

    def __init__(self, **kwargs):
        """Construct new transformer for entry list."""
        super(ManyTransformer, self).__init__(**kwargs)
        self.mapping = OrderedDict((
            (i.set_name, self.create_child_transformer(i))
            for i in self.supported_models
        ))


# pylint: disable=too-few-public-methods
class SupportedModelsMixin(object):
    """Mixin to keep sync models."""

    @property
    def supported_models(self):
        """Return model tuple to sync."""
        sync_keys = self.account_manager.get_settings()['synchronize_key']
        if sync_keys:
            return (
                SshKey, Snippet,
                Identity, SshConfig,
                Tag, Group,
                Host, PFRule,
                TagHost
            )
        else:
            return (
                Snippet, SshConfig,
                Tag, Group,
                Host, PFRule,
                TagHost
            )


class BulkTransformer(CryptoChildTransformerCreatorMixin,
                      GetPrimaryKeyTransformerMixin,
                      SupportedModelsMixin,
                      ManyTransformer):
    """Transformer for entry list."""

    child_transformer_class = CryptoBulkEntryTransformer

    def __init__(self, crypto_controller, **kwargs):
        """Construct new transformer for entry list."""
        self.crypto_controller = crypto_controller
        super(BulkTransformer, self).__init__(**kwargs)
        self.deleted_sets_transformer = DeleteSetsTransformer(
            storage=self.storage, account_manager=self.account_manager
        )

    def to_model(self, payload):
        """Convert payload with set list."""
        models = {}
        models['last_synced'] = payload.pop('now')
        deleted_sets = payload.pop('deleted_sets')
        for set_name, transformer in self.mapping.items():
            models[set_name] = [
                transformer.to_model(i) for i in payload[set_name]
            ]

        models['deleted_sets'] = self.deleted_sets_transformer.to_model(
            deleted_sets
        )
        return models

    def to_payload(self, model):
        """Convert model to payload with set list."""
        payload = {}
        payload['last_synced'] = model.pop('last_synced')
        payload['delete_sets'] = self.deleted_sets_transformer.to_payload(None)
        for set_name, transformer in self.mapping.items():
            internal_model = self.storage.filter(
                transformer.model_class, any,
                **{
                    'remote_instance.state.rcontains': ['created', 'updated'],
                    'remote_instance': None
                }
            )
            payload[set_name] = [
                transformer.to_payload(i) for i in internal_model
            ]
        return payload


class DeleteSetsTransformer(GetPrimaryKeyTransformerMixin,
                            SupportedModelsMixin,
                            ManyTransformer):
    """Transformer for deleted_sets field."""

    @property
    def supported_models(self):
        """Return model tuple to sync."""
        return reversed(
            super(DeleteSetsTransformer, self).supported_models
        )

    def create_child_transformer(self, model):
        """Create transformer for sub transformers."""
        return self.get_primary_key_transformer(model)

    def to_model(self, payload):
        """Handle payload to local models and delete them completely."""
        model = {}
        for set_name, transformer in self.mapping.items():
            deleted_set_with_none = [
                self._map_remote_id_to_model(transformer, i)
                for i in payload[set_name]
            ]
            deleted_set = [i for i in deleted_set_with_none if i]
            model[set_name] = deleted_set
            self.soft_delete_entries(deleted_set)
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
    def _map_remote_id_to_model(self, transformer, remote_id):
        try:
            return transformer.to_model(remote_id)
        except (DoesNotExistException, SkipField):
            return None
