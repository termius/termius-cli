# -*- coding: utf-8 -*-
from operator import attrgetter, itemgetter


def map_zip_model_fields(model, field_getter=None):
    """Return list of tuples (field_object, field_value)."""
    field_getter = field_getter or attrgetter(model.fields)
    return zip(model.fields, field_getter(model))


id_getter = itemgetter('id')
