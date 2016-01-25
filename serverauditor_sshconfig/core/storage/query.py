import operator


class QueryOperator(object):

    operators = ['eq', 'ne', 'gt', 'lt', 'le', 'ge']

    def __init__(self, field, value):
        splited_field = field.split('.')
        operator_name = splited_field[-1]
        if operator_name not in self.operators:
            operator_name = 'eq'
            self.get_field = operator.attrgetter(field)
        else:
            self.get_field = operator.attrgetter('.'.join(splited_field[:-1]))

        self.operator = getattr(operator, operator_name)
        self.value = value

    def __call__(self, obj):
        try:
            field = self.get_field(obj)
        except AttributeError:
            return False
        return self.operator(field, self.value)


class Query(object):

    def __init__(self, union=None, **kwargs):
        self.operators_union = union or all
        self.operators = [
            QueryOperator(k, v) for k, v in kwargs.items()
        ]

    def __call__(self, obj):
        filters = [i(obj) for i in self.operators]
        result = self.operators_union(filters)
        return result
