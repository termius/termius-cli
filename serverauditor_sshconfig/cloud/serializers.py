"""Serializers (read controllers) is like django rest framework serializers."""

import six
import abc
from collections import OrderedDict
from operator import attrgetter, itemgetter
from ..core.models import RemoteInstance
from ..core.exceptions import DoesNotExistException
from .models import (
    Host, Group,
    Tag, SshKey,
    SshIdentity, SshConfig,
    Group, Host,
    PFRule, TagHost,
)


def zip_model_fields(model, field_getter=None):
    field_getter = field_getter or attrgetter(model.fields)
    return zip(model.fields, field_getter(model))


@six.add_metaclass(abc.ABCMeta)
class Serializer(object):

    def __init__(self, storage):
        assert storage
        self.storage = storage

    @abc.abstractmethod
    def to_model(self, payload):
        """Convert REST API payload to Application models."""

    @abc.abstractmethod
    def to_payload(self, model):
        """Convert Application models to REST API payload."""


class BulkEntryBaseSerializer(Serializer):

    def __init__(self, model_class, **kwargs):
        super(BulkEntryBaseSerializer, self).__init__(**kwargs)
        assert model_class
        self.model_class = model_class


class BulkPrimaryKeySerializer(BulkEntryBaseSerializer):

    to_model_mapping = {
        int: int,
        dict: itemgetter('id')
    }

    def id_from_payload(self, payload):
        return self.to_model_mapping[type(payload)](payload)

    def to_model(self, payload):
        if not payload:
            return None

        remote_instance_id = self.id_from_payload(payload)

        model = self.storage.get(
            self.model_class,
            **{'remote_instance.id': remote_instance_id}
        )
        return model

    def to_payload(self, model):
        if not model:
            return None
        if model.remote_instance:
            return model.remote_instance.id
        else:
            return '{model.set_name}/{model.id}'.format(model=model)


class BulkEntrySerializer(BulkPrimaryKeySerializer):

    def __init__(self, **kwargs):
        super(BulkEntrySerializer, self).__init__(**kwargs)
        self.attrgetter = attrgetter(*self.model_class.fields)
        self.remote_instance_attrgetter = attrgetter(*RemoteInstance.fields)

    def update_model_fields(self, model, payload):
        for i in model.fields:
            mapping = model.mapping.get(i)
            if mapping:
                serializer = BulkPrimaryKeySerializer(
                    storage=self.storage, model_class=mapping.model
                )
                field = serializer.to_model(payload[i])
            else:
                field = payload[i]
            setattr(model, i, field)
        return model

    def create_remote_instance(self, payload):
        remote_instance = RemoteInstance()
        for i in RemoteInstance.fields:
            setattr(remote_instance, i, payload.pop(i))
        return remote_instance

    def get_or_initialize_model(self, payload):
        try:
            model = super(BulkEntrySerializer, self).to_model(payload)
        except DoesNotExistException:
            remote_instance = self.create_remote_instance(payload)
            model = self.model_class()
            model.remote_instance = remote_instance
            model.update(
                ((k, v) for k, v in payload.items() if k in model.fields)
            )

        model.id = payload.get('local_id', model.id)
        return model

    def to_model(self, payload):
        model = self.get_or_initialize_model(payload)
        model = self.update_model_fields(model, payload)
        return model

    def to_payload(self, model):
        payload = dict(zip_model_fields(model, self.attrgetter))
        if model.remote_instance:
            zipped_remote_instance = zip_model_fields(
                model.remote_instance, self.remote_instance_attrgetter
            )
            payload.update(zipped_remote_instance)
        payload['local_id'] = model.id
        for field, mapping in model.mapping.items():
            serializer = BulkPrimaryKeySerializer(
                storage=self.storage, model_class=mapping.model
            )
            fk_payload = serializer.to_payload(getattr(model, field))
            payload[field] = fk_payload
        return payload

class CryptoBulkEntrySerializer(BulkEntrySerializer):

    def __init__(self, crypto_controller, **kwargs):
        super(CryptoBulkEntrySerializer, self).__init__(**kwargs)
        self.crypto_controller = crypto_controller

    def to_model(self, payload):
        model = super(CryptoBulkEntrySerializer, self).to_model(payload)
        return self.crypto_controller.decrypt(model)

    def to_payload(self, model):
        encrypted_model = self.crypto_controller.encrypt(model)
        return super(CryptoBulkEntrySerializer, self).to_payload(
            encrypted_model)


class BulkSerializer(Serializer):

    child_serializer_class = CryptoBulkEntrySerializer
    supported_models = (
        SshKey, SshIdentity, SshConfig, Tag, Group, Host, PFRule, TagHost
    )

    def create_child_serializer(self, model_class):
        return self.child_serializer_class(
            model_class=model_class, storage=self.storage,
            crypto_controller=self.crypto_controller
        )

    def __init__(self, crypto_controller, **kwargs):
        super(BulkSerializer, self).__init__(**kwargs)
        self.crypto_controller = crypto_controller
        self.mapping = OrderedDict((
            (i.set_name, self.create_child_serializer(i))
            for i in self.supported_models
        ))

    def process_model_entries(self, updated, deleted):
        for i in updated:
            self.storage.save(i)
        for i in deleted:
            self.storage.delete(i)

    def to_model(self, payload):
        models = {}
        models['last_synced'] = payload.pop('now')
        models['deleted_sets'] = {}
        deleted_sets = payload.pop('deleted_sets')
        for set_name, serializer in self.mapping.items():
            models[set_name] = [serializer.to_model(i) for i in payload[set_name]]
            serializer = BulkPrimaryKeySerializer(
                storage=self.storage, model_class=serializer.model_class
            )
            deleted_set = []
            for i in deleted_sets[set_name]:
                try:
                    deleted_set.append(serializer.to_model(i))
                except DoesNotExistException:
                    pass
            models['deleted_sets'][set_name] = deleted_set

            self.process_model_entries(
                models[set_name], models['deleted_sets'][set_name]
            )
        return models

    def to_payload(self, model):
        payload = {}
        payload['last_synced'] = model.pop('last_synced')
        deleted_sets = payload.pop('deleted_sets')
        for set_name, serializer in self.mapping.items():
            payload[set_name] = [serializer.to_model(i) for i in payload[set_name]]
        raise RuntimeError('Need implement deleted_sets showing.')
