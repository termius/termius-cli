# -*- coding: utf-8 -*-
"""Module with PFRule commands."""
import re
from operator import attrgetter
from cached_property import cached_property
from ..core.exceptions import InvalidArgumentException
from ..core.commands import DetailCommand, ListCommand
from ..core.commands.single import RequiredOptions
from ..core.models.terminal import Host, PFRule


class PFRuleCommand(DetailCommand):
    """work with a port forwarding rule"""

    model_class = PFRule
    required_options = RequiredOptions(create=('host', 'binding', 'pf_type'))

    @cached_property
    def fields(self):
        """Return dictionary of args serializers to models field."""
        _fields = {
            i: attrgetter(i) for i in ('pf_type', 'label',)
        }
        _fields['host'] = self.get_safely_instance_partial(Host, 'host')
        return _fields

    @property
    # pylint: disable=no-self-use
    def binding_parsers(self):
        """Return binding parser per type abbreviation."""
        return {
            'Dynamic Rule': BindingParser.dynamic,
            'Local Rule': BindingParser.local,
            'Remote Rule': BindingParser.remote,
        }

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-H', '--host', metavar='ID or NAME',
            help='create port forwarding rule for the host with ID or NAME'
        )
        parser.add_argument(
            '--dynamic', dest='pf_type', action='store_const',
            const='Dynamic Rule', help='dynamic port forwarding'
        )
        parser.add_argument(
            '--remote', dest='pf_type', action='store_const',
            const='Remote Rule', help='remote port forwarding'
        )
        parser.add_argument(
            '--local', dest='pf_type', action='store_const',
            const='Local Rule', help='local port forwarding'
        )
        parser.add_argument(
            '--binding', metavar='BINDINGS',
            help=('specify binding of ports and addresses '
                  '[bind_address:]port or [bind_address:]port:host:hostport')
        )
        return parser

    def parse_binding(self, pf_type, binding):
        """Parse binding string to dict."""
        return self.binding_parsers[pf_type](binding)

    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        instance = super(PFRuleCommand, self).serialize_args(args, instance)
        if args.binding:
            binding_dict = self.parse_binding(instance.pf_type, args.binding)
            for key, value in binding_dict.items():
                setattr(instance, key, value)
        return instance


class PFRulesCommand(ListCommand):
    """list all port forwarding rules"""

    model_class = PFRule


class InvalidBinding(InvalidArgumentException):
    """Raise it when binding can not be parsed."""

    pass


class BindingParser(object):
    """Binding string parser.

    Binding string is string like '[localhost:]localport:hostanme:remote port'.
    """

    local_pf_re = re.compile(
        r'^((?P<bound_address>[\w.]+):)?(?P<local_port>\d+)'
        r':(?P<hostname>[\w.]+):(?P<remote_port>\d+)$'
    )
    dynamic_pf_re = re.compile(
        r'^((?P<bound_address>[\w.]+):)?(?P<local_port>\d+)'
        r'(?P<hostname>)(?P<remote_port>)$'
        # Regexp Groups should be the same for all rules.
    )

    @classmethod
    def patch_ports(cls, pair):
        """Wrap ports with int or use None."""
        if pair[0] in ('remote_port', 'local_port'):
            return pair[0], pair[1] and int(pair[1]) or None
        return pair

    @classmethod
    def _parse(cls, regexp, binding_str):
        matched = regexp.match(binding_str)
        if not matched:
            raise InvalidBinding('Invalid binding format.')
        return dict([cls.patch_ports(i) for i in matched.groupdict().items()])

    @classmethod
    def local(cls, binding_str):
        """Parse local port forwarding binding string to dict."""
        return cls._parse(cls.local_pf_re, binding_str)
    remote = local
    """Parse remote port forwarding binding string to dict."""

    @classmethod
    def dynamic(cls, binding_str):
        """Parse dynamic port forwarding binding string to dict."""
        return cls._parse(cls.dynamic_pf_re, binding_str)
