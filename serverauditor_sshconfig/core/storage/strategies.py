import six
from ..models import DeleteSets


# pylint: disable=too-few-public-methods
class Strategy(object):

    def __init__(self, storage):
        self.storage = storage


class SaveStrategy(Strategy):

    # pylint: disable=no-self-use,unused-argument
    def save_submodel(self, submodel, mapping):
        if isinstance(submodel, six.integer_types):
            return submodel
        assert submodel.id
        return submodel.id

    def save_field(self, field, mapping):
        return field and self.save_submodel(field, mapping)

    def save(self, model):
        model_copy = model.copy()
        fk_fields = model.fk_field_names()
        for field in fk_fields:
            mapping = model.fields[field]
            saved_submodel = self.save_field(getattr(model, field), mapping)
            setattr(model_copy, field, saved_submodel)
        return model_copy


class RelatedSaveStrategy(SaveStrategy):

    def save_submodel(self, submodel, mapping):
        return self.storage.save(submodel).id


class GetStrategy(Strategy):

    # pylint: disable=no-self-use
    def get(self, model):
        return model


class RelatedGetStrategy(GetStrategy):

    def get(self, model):
        result = super(RelatedGetStrategy, self).get(model)
        fk_fields = model.fk_field_names()
        for field in fk_fields:
            mapping = model.fields[field]
            submodel_id = getattr(result, field)
            if submodel_id:
                submodel = self.storage.get(mapping.model, id=submodel_id)
                setattr(result, field, submodel)
        return result


class DeleteStrategy(Strategy):

    # pylint: disable=no-self-use
    def get_delete_sets(self):
        return {}

    # pylint: disable=no-self-use
    def delete(self, model):
        return model

    def confirm_delete(self, deleted_sets):
        pass


class SoftDeleteStrategy(DeleteStrategy):

    delete_sets_class = DeleteSets

    def get_delete_sets(self):
        try:
            data = self.storage.low_get(self.delete_sets_class.set_name)
        except KeyError:
            data = {}
        model = self.delete_sets_class(data)
        return model

    def set_delete_sets(self, deleted):
        self.storage.low_set(self.delete_sets_class.set_name, deleted)

    def delete(self, model):
        delete_sets = self.get_delete_sets()
        delete_sets.soft_delete(model)
        self.set_delete_sets(delete_sets)
        return model

    def confirm_delete(self, sets):
        # FIXME It needs more suitable name
        delete_sets = self.get_delete_sets()
        for key, value in sets.items():
            for i in value:
                delete_sets.delete_soft_deleted(key, i)
        self.set_delete_sets(delete_sets)
