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
            self.fail_not_exist(model_class)
        except TooManyEntriesException:
            self.fail_too_many(model_class)

    def fail_not_exist(self, model_class):
        raise ArgumentRequiredException(
            'Not found any {} instance.'.format(model_class)
        )

    def fail_too_many(self, model_class):
        raise ArgumentRequiredException(
            'Found too many {} instances.'.format(model_class)
        )


class InstanceOpertionMixin(object):

    def create_instance(self, args):
        """Create new model entry."""
        instance = self.serialize_args(args)
        with self.storage:
            saved_instance = self.storage.save(instance)
        self.log_create(saved_instance)

    def update_instance(self, args, instance):
        """Update model entry."""
        updated_instance = self.serialize_args(args, instance)
        with self.storage:
            self.storage.save(updated_instance)
            self.log_update(updated_instance)

    def delete_instance(self, instance):
        """Delete model entry."""
        with self.storage:
            self.storage.delete(instance)
            self.log_delete(instance)

    def log_create(self, entry):
        """Log creating new model entry."""
        self.app.stdout.write('{}\n'.format(entry.id))
        self.log.info('Create object.')

    def log_update(self, entry):
        """Log updating model entry."""
        self.app.stdout.write('{}\n'.format(entry.id))
        self.log.info('Update object.')

    def log_delete(self, entry):
        """Log deleting model entry."""
        self.app.stdout.write('{}\n'.format(entry.id))
        self.log.info('Delete object.')
