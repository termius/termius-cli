# -*- coding: utf-8 -*-
""""Package to keep storage id generating logic."""
from uuid import uuid4


# pylint: disable=too-few-public-methods
class UUIDGenerator(object):
    """ID generator based on uuid4."""

    def __init__(self, storage):
        """Contruct IDGenerator.

        :param ApplicationStorage storage: Storage instance
        """
        self.storage = storage

    def __call__(self, model):
        """Generate id.

        :param core.models.Model model: generate and set id for this Model.
        """
        assert not getattr(model, model.id_name)
        identificator = uuid4().time_low
        setattr(model, model.id_name, identificator)
        return identificator
