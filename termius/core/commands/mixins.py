# -*- coding: utf-8 -*-
"""Module with different CLI commands mixins."""
import getpass
import os
from operator import attrgetter
from functools import partial
from cached_property import cached_property
from ..exceptions import (
    DoesNotExistException, ArgumentRequiredException,
    TooManyEntriesException, SkipField
)
from ..models.terminal import SshConfig, Identity
from .utils import parse_ids_names, DefaultAttrGetter
from ..models.utils import GroupStackGenerator, Merger


# pylint: disable=too-few-public-methods
class PasswordPromptMixin(object):
    """Mixin to command to call account password prompt."""

    # pylint: disable=no-self-use
    def prompt_password(self):
        """Ask user to enter password in secure way."""
        return getpass.getpass('Password:')


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
            'Not found any {} instance.'.format(model_class.__name__.lower())
        )

    # pylint: disable=no-self-use
    def fail_too_many(self, model_class):
        """Raise an error about too many instances."""
        raise ArgumentRequiredException(
            'Found too many {} instances.'.format(model_class.__name__.lower())
        )

    def get_safely_instance(self, model_class, arg):
        """Provide safer way to get relations."""
        return arg and self.get_relation(model_class, arg)

    def get_safely_instance_partial(self, model, arg_name):
        """Return wrap get_safely_instance() with partial for arg_name."""
        return partial(self._safely_instance, model=model, arg_name=arg_name)

    def _safely_instance(self, args, model, arg_name):
        value = getattr(args, arg_name)
        return self.get_safely_instance(model, value)


class PrepareResultMixin(object):
    """Mixin with method to transform dict-list to 2-size tuple."""

    @property
    def prepare_fields(self):
        """Return fields for model."""
        return self.model_class.allowed_fields()

    def prepare_result(self, found_list):
        """Return tuple with data in format for Lister."""
        fields = sorted(list(set(self.prepare_fields) - set(self.skip_fields)))
        getter = DefaultAttrGetter(*fields)
        return fields, [getter(i) for i in found_list]


class SshConfigPrepareMixin(PrepareResultMixin):
    """Mixin with methods to render ssh config and identity fields."""

    @property
    def prepare_fields(self):
        """Return fields for model."""
        return (
            self.instance_fields +
            self.ssh_config_fields +
            self.identity_fields
        )

    @property
    def instance_fields(self):
        """Return instance fields."""
        return [
            i for i in list(self.model_class.allowed_fields())
            if i != 'ssh_config'
        ]

    @property
    def ssh_config_fields(self):
        """Return ssh config fields."""
        fields = SshConfig.allowed_fields()
        field_format = 'ssh_config.{}'.format
        return [
            field_format(i) for i in fields
            if i != 'identity'
        ]

    @property
    def identity_fields(self):
        """Return identity fields."""
        fields = Identity.allowed_fields()
        field_format = 'ssh_config.identity.{}'.format
        return [
            field_format(i) for i in fields
            if i != 'identity'
        ]


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


class ArgModelSerializerMixin(object):
    """Class to keep logic of command line args serialization to model."""

    @cached_property
    def fields(self):
        """Return dictionary of args serializers to models field."""
        return {
            i: attrgetter(i) for i in self.model_class.fields
        }

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        instance = instance or self.model_class()
        for i in self.model_class.fields:
            try:
                value = self.fields[i](args)
            except (SkipField, KeyError):
                continue
            if value is not None:
                setattr(instance, i, value)
        self.validate(instance)
        return instance

    # pylint: disable=unused-argument
    def validate(self, instance):
        """Validate models fields before saving."""
        return instance

    # pylint: disable=unused-argument
    def skip(self, args):
        """Call to skip field serialization."""
        raise SkipField()


class InstanceOperationMixin(ArgModelSerializerMixin, object):
    """Mixin with methods to create, update and delete operations."""

    def create_instance(self, args):
        """Create new model entry."""
        instance = self.serialize_args(args)
        with self.storage:
            self.pre_save(instance)
            saved_instance = self.storage.save(instance)
            instance.id = saved_instance.id
            self.update_children(instance, args)
        self.log_create(saved_instance)

    def update_instance(self, args, instance):
        """Update model entry."""
        instance = self.serialize_args(args, instance)
        with self.storage:
            self.pre_save(instance)
            self.storage.save(instance)
            self.update_children(instance, args)
        self.log_update(instance)

    # pylint: disable=no-self-use,unused-argument
    def pre_save(self, instance):
        """Patch instance fields before saving."""
        pass

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
        self._general_log(entry, 'Entry created.')

    def log_update(self, entry):
        """Log updating model entry."""
        self._general_log(entry, 'Entry updated.')

    def log_delete(self, entry):
        """Log deleting model entry."""
        self._general_log(entry, 'Entry deleted.')

    def _general_log(self, entry, message):
        if os.getenv('TERMIUS_CLI_DEBUG'):
            self.app.stdout.write('{}\n'.format(entry.id))

        self.log.info(message)


class GroupStackGetterMixin(object):
    """Mixin to get whole stack of parent groups."""

    # pylint: disable=no-self-use
    def get_group_stack(self, instance):
        """Generate parent group stack for instance."""
        stack_generator = GroupStackGenerator(instance)
        return stack_generator.generate()


class SshConfigMergerMixin(GroupStackGetterMixin, object):
    """Mixin to squash (aka merge) stack to single ssh config."""

    def get_merged_ssh_config(self, instance):
        """Get merged ssh config instance for instance.

        :param instance: Host or Group instance.
        """
        group_stack = self.get_group_stack(instance)
        full_stack = [instance] + group_stack
        return self.merge_ssh_config(full_stack)

    def merge_ssh_config(self, full_stack):
        """Squash full_stack to single ssh_config instance."""
        ssh_config_merger = self.get_ssh_config_merger(full_stack)
        identity_merger = self.get_identity_merger(ssh_config_merger)
        ssh_config = ssh_config_merger.merge()
        visible_identity = self.get_visible_identity(ssh_config_merger)
        if visible_identity:
            ssh_config.identity = visible_identity
        else:
            ssh_config.identity = identity_merger.merge()
        return ssh_config

    # pylint: disable=no-self-use
    def get_ssh_config_merger(self, stack):
        """Create ssh config merger for passed stack."""
        return Merger(stack, 'ssh_config', SshConfig())

    # pylint: disable=no-self-use
    def get_visible_identity(self, ssh_config_merger):
        """Return first of visible identity."""
        stack = [
            i.identity for i in ssh_config_merger.get_entry_stack()
            if i.identity.is_visible
        ]
        return (stack and stack[0]) or None

    # pylint: disable=no-self-use
    def get_identity_merger(self, ssh_config_merger):
        """Create identity merger for passed merger."""
        stack = [
            i for i in ssh_config_merger.get_entry_stack()
            if not i.identity.is_visible
        ]
        return Merger(stack, 'identity', Identity())
