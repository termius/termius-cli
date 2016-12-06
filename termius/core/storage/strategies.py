# -*- coding: utf-8 -*-
"""Module with strategies.

Strategy is some additional behaviour for storage.
"""
import six
from ..models.base import DeleteSets


# pylint: disable=too-few-public-methods
class Strategy(object):
    """Base class for any strategy."""

    def __init__(self, storage):
        """Construct strategy, keep assigned storage."""
        self.storage = storage


class SaveStrategy(Strategy):
    """Saver strategy that saves relations on storage."""

    # pylint: disable=no-self-use,unused-argument
    def save_submodel(self, submodel, mapping):
        """Save submodels of model."""
        if isinstance(submodel, six.integer_types):
            return submodel
        assert submodel.id
        return submodel.id

    def serialize_relation(self, field, mapping):
        """Transform relation field.

        Use it to save relations.
        """
        return field and self.save_submodel(field, mapping)

    def mark_model(self, model):
        """Change model state before saving."""
        model.mark_updated()

    def save(self, model):
        """Do extra action when model saved.

        Save it's relations.
        """
        model_copy = model.copy()
        fk_fields = model.fk_field_names()
        for field in fk_fields:
            mapping = model.fields[field]
            saved_submodel = self.serialize_relation(
                getattr(model, field), mapping
            )
            setattr(model_copy, field, saved_submodel)
        return model_copy


class RelatedSaveStrategy(SaveStrategy):
    """Saver strategy that does not save relations."""

    def save_submodel(self, submodel, mapping):
        """Do not save any, barely return relation id."""
        return self.storage.save(submodel).id


class SyncSaveStrategy(SaveStrategy):
    """Saver strategy for synced models."""

    def mark_model(self, model):
        """Change model state before saving."""
        model.mark_synced()


class GetStrategy(Strategy):
    """Getter strategy that simply get model."""

    # pylint: disable=no-self-use
    def get(self, model):
        """Return what it gets."""
        return model


class RelatedGetStrategy(GetStrategy):
    """Getter strategy that get model's relation tree."""

    def get(self, model):
        """Return model with whole relation tree."""
        result = super(RelatedGetStrategy, self).get(model)
        fk_fields = model.fk_field_names()
        for field in fk_fields:
            mapping = model.fields[field]
            submodel_id = getattr(result, field)
            if submodel_id:
                submodel = self.storage.get_single_by_id(
                    mapping.model, submodel_id
                )
                setattr(result, field, submodel)
        return result


class DeleteStrategy(Strategy):
    """Deleter strategy that completely delete model."""

    # pylint: disable=no-self-use
    def get_delete_sets(self):
        """Return delete objects."""
        return {}

    # pylint: disable=no-self-use
    def delete(self, model):
        """Return what it gets."""
        return model

    def remove_intersection(self, deleted_sets):
        """Confirm delete (Need to create more suitable description)."""
        pass


class SoftDeleteStrategy(DeleteStrategy):
    """Deleter strategy that delete model and do small extra action.

    Extra action is that store model remote id in deleted_sets if any.
    """

    delete_sets_class = DeleteSets

    def get_delete_sets(self):
        """Retrieve delete objects from storage."""
        try:
            data = self.storage.low_get(self.delete_sets_class.set_name)
        except KeyError:
            data = {}
        model = self.delete_sets_class(data)
        return model

    def set_delete_sets(self, deleted):
        """Store delete sets into the storage."""
        self.storage.low_set(self.delete_sets_class.set_name, deleted)

    def delete(self, model):
        """Store remote_id of model in delete sets."""
        delete_sets = self.get_delete_sets()
        delete_sets.store(model)
        self.set_delete_sets(delete_sets)
        return model

    def remove_intersection(self, sets):
        """Remove from deleted_sets intersection with sets passed."""
        delete_sets = self.get_delete_sets()
        for set_name, id_list in sets.items():
            delete_sets.remove_all(set_name, id_list)
        self.set_delete_sets(delete_sets)
