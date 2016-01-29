# -*- coding: utf-8 -*-
"""Module with different CLI commands mixins."""
import getpass
from ..exceptions import (
    DoesNotExistException, ArgumentRequiredException,
    TooManyEntriesException
)


# pylint: disable=too-few-public-methods
class PasswordPromptMixin(object):
    """Mixin to command to call account password prompt."""

    # pylint: disable=no-self-use
    def prompt_password(self):
        """Ask user to enter password in secure way."""
        return getpass.getpass("Serverauditor's password:")


class GetRelationMixin(object):
    """Mixin that add way to retrieve entry per id or name."""

    def get_relation(self, model_class, arg):
        """Retrieve relation object from storage."""
        try:
            relation_id = int(arg)
        except ValueError:
            relation_id = None
        try:
            return self.storage.get(model_class, query_union=any,
                                    id=relation_id, label=arg)
        except DoesNotExistException:
            raise ArgumentRequiredException(
                'Not found any {} instance.'.format(model_class)
            )
        except TooManyEntriesException:
            raise ArgumentRequiredException(
                'Found to many {} instances.'.format(model_class)
            )
