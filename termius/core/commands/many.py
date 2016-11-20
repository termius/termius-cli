# -*- coding: utf-8 -*-
"""Module with base commands for list entries."""
# pylint: disable=import-error
from cliff.lister import Lister
from .base import AbstractCommand
from .mixins import GetRelationMixin, PrepareResultMixin


# pylint: disable=too-few-public-methods, abstract-method
class ListCommand(GetRelationMixin, PrepareResultMixin,
                  AbstractCommand, Lister):
    """Command for listing storage content."""

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        instances = self.storage.get_all(self.model_class)
        return self.prepare_result(instances)
