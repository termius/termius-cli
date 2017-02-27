# -*- coding: utf-8 -*-
"""Transformers is like django rest framework transformer."""
import abc
import six
from ....core.exceptions import TermiusException


@six.add_metaclass(abc.ABCMeta)
class Transformer(object):
    """Base transformer."""

    # pylint: disable=unused-argument
    def __init__(self, storage, account_manager, **kwargs):
        """Create new Transformer."""
        assert storage
        self.storage = storage
        self.account_manager = account_manager

    @abc.abstractmethod
    def to_model(self, payload):
        """Convert REST API payload to Application models."""

    @abc.abstractmethod
    def to_payload(self, model):
        """Convert Application models to REST API payload."""


class DeletBadEncrypted(TermiusException):
    """Raise it when badly encrypted is founded and cleaning is required."""

    def __init__(self, model):
        """Create new exception and keep model for reuse."""
        self.model = model
