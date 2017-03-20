# -*- coding: utf-8 -*-
"""Module with utils for terminal models."""
import functools
from operator import attrgetter
from .terminal import Host


class GroupStackGenerator(object):
    """Class to keep parent group stack generation."""

    group_getter = attrgetter('parent_group')

    def __init__(self, instance):
        """Construct new generator instance."""
        if isinstance(instance, Host):
            self.root_group = instance.group
        else:
            self.root_group = instance.parent_group
        self.instance = instance

    def generate(self):
        """Generate list (aka stack) of parent groups."""
        return list(self.iterate_groups())

    def iterate_groups(self):
        """Iterator over instances parent groups."""
        group = self.root_group
        while group:
            yield group
            group = self.group_getter(group)


class Merger(object):
    """Class to process ssh config merging."""

    def __init__(self, stack, stack_field, initial):
        """Construct new instance stack."""
        self.stack = stack
        self.stack_field = stack_field
        self.merge_field_list = initial.mergable_fields
        self.stack_field_getter = attrgetter(stack_field)
        self.initial = initial

    def get_entry_stack(self):
        """Generate entries stack from parent stack."""
        not_filtered = [self.stack_field_getter(i) for i in self.stack]
        return [i for i in not_filtered if i]

    def merge(self):
        """Merge instances of full_stack to single instance."""
        entries = self.get_entry_stack()
        merged = functools.reduce(self.reducer, entries, self.initial)
        return merged

    def reducer(self, accumulator, value):
        """Merge value fields to accumulator."""
        for i in self.merge_field_list:
            merge_field(accumulator, value, i)
        return accumulator


def merge_field(left, right, field):
    """Merge field of right instance to left one."""
    left_field = getattr(left, field)
    if not left_field:
        setattr(left, field, getattr(right, field))
