# -*- coding: utf-8 -*-
"""Module with different CLI commands mixins."""
import getpass
from operator import attrgetter
from ..exceptions import (
    DoesNotExistException, ArgumentRequiredException,
    TooManyEntriesException
)
from .utils import parse_ids_names


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

    # pylint: disable=no-self-use
    def fail_not_exist(self, model_class):
        """Raise an error about not existed instance."""
        raise ArgumentRequiredException(
            'Not found any {} instance.'.format(model_class)
        )

    # pylint: disable=no-self-use
    def fail_too_many(self, model_class):
        """Raise an error about too many instances."""
        raise ArgumentRequiredException(
            'Found too many {} instances.'.format(model_class)
        )


class PrepareResultMixin(object):
    """Mixin with method to transform dict-list to 2-size tuple."""

    def prepare_result(self, found_list):
        """Return tuple with data in format for Lister."""
        fields = self.model_class.allowed_fields()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in found_list]


class GetObjectsMixin(object):
    """Mixin with method to list objects with ids or name list."""

    def get_objects(self, ids__names):
        """Get model list.

        Models will match id and label with passed ids__names list.
        """
        ids, names = parse_ids_names(ids__names)
        instances = self.storage.filter(
            self.model_class, any,
            **{'id.rcontains': ids, 'label.rcontains': names}
        )
        if not instances:
            raise DoesNotExistException("There aren't any instance.")
        return instances


class InstanceOpertionMixin(object):
    """Mixin with methods to create, update and delete operations."""

    def create_instance(self, args):
        """Create new model entry."""
        instance = self.serialize_args(args)
        with self.storage:
            saved_instance = self.storage.save(instance)
            instance.id = saved_instance.id
            self.update_children(instance, args)
        self.log_create(saved_instance)

    def update_instance(self, args, instance):
        """Update model entry."""
        updated_instance = self.serialize_args(args, instance)
        with self.storage:
            self.storage.save(updated_instance)
            self.update_children(updated_instance, args)
            self.log_update(updated_instance)

    def update_children(self, instance, args):
        """Update children of instance.

        It's called while create and update instance.
        """
        pass

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
