# -*- coding: utf-8 -*-
"""Module tool heplers to parse command lines."""
from collections import OrderedDict
from operator import attrgetter


# pylint: disable=no-self-use
def parse_ids_names(ids__names):
    """Parse ids__models list."""
    ids = [int(i) for i in ids__names if i.isdigit()]
    return ids, ids__names


# pylint: disable=too-few-public-methods
class DefaultAttrGetter(object):
    """Class implement attrgetter with silent fail logic to return None."""

    def __init__(self, *attrs):
        """Construct new instance."""
        self.getattrs = OrderedDict((
            (i, attrgetter(i)) for i in attrs
        ))

    def __call__(self, instance):
        """Get attributes from instance."""
        return [
            self.get_attr_with_default(instance, i, None)
            for i in self.getattrs
        ]

    def get_attr_with_default(self, instance, field, default):
        """Return attr value or None if fail."""
        try:
            return self.getattrs[field](instance)
        # pylint: disable=broad-except
        except Exception:
            return default
