# -*- coding: utf-8 -*-
"""Serializers (read controllers) is like django rest framework serializers."""
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Serializer(object):
    """Base serializer."""

    def __init__(self, storage):
        """Create new Serializer."""
        assert storage
        self.storage = storage

    @abc.abstractmethod
    def to_model(self, payload):
        """Convert REST API payload to Application models."""

    @abc.abstractmethod
    def to_payload(self, model):
        """Convert Application models to REST API payload."""
        pass
