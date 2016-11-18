# -*- coding: utf-8 -*-
"""Package with Query classes."""
from . import operators


# pylint: disable=too-few-public-methods
class QueryOperator(object):
    """Operators for list's filtering."""

    operators = ['eq', 'ne', 'gt', 'lt', 'le', 'ge', 'rcontains', 'contains']

    def __init__(self, field, value):
        """Construct new operator."""
        splited_field = field.split('.')
        operator_name = splited_field[-1]

        if operator_name not in self.operators:
            operator_name = 'eq'
            self.get_field = operators.attrgetter(field)
        else:
            self.get_field = operators.attrgetter('.'.join(splited_field[:-1]))

        self.operator = getattr(operators, operator_name)
        self.value = value

    def __call__(self, obj):
        """Filter single object."""
        try:
            field = self.get_field(obj)
        except AttributeError:
            return False
        return self.operator(field, self.value)


# pylint: disable=too-few-public-methods
class Query(object):
    """Query construction class (aka set of operators)."""

    def __init__(self, union=None, **kwargs):
        """Construct new query."""
        self.operators_union = union or all
        self.operators = [
            QueryOperator(k, v) for k, v in kwargs.items()
        ]

    def __call__(self, obj):
        """Call all operators for object and union results."""
        filters = [i(obj) for i in self.operators]
        result = self.operators_union(filters)
        return result
