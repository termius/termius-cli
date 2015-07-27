import re
from base64 import b64decode
from operator import attrgetter
from ..core.commands import AbstractCommand, DetailCommand, ListCommand
from .controllers import ApiController
from .cryptor import RNCryptor
from .models import Host, SshConfig, SshIdentity, SshKey, Tag, Group, PFRule


class PushCommand(AbstractCommand):

    """Push data to Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PushCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--strategy', metavar='STRATEGY_NAME',
            help='Force to use specific strategy to merge data.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Push data to Serverauditor cloud.')


class PullCommand(AbstractCommand):

    """Pull data from Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PullCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--strategy', metavar='STRATEGY_NAME',
            help='Force to use specific strategy to merge data.'
        )
        return parser

    def take_action(self, parsed_args):
        encryption_salt = b64decode(self.config.get('User', 'salt'))
        hmac_salt = b64decode(self.config.get('User', 'hmac_salt'))
        password = self.prompt_password()
        cryptor = RNCryptor()
        cryptor.password = password
        cryptor.encryption_salt = encryption_salt
        cryptor.hmac_salt = hmac_salt
        controller = ApiController(self.storage, self.config, cryptor)
        with self.storage:
            controller.get_bulk()
        self.log.info('Pull data from Serverauditor cloud.')


class UseGroupCommand(AbstractCommand):

    """Change group."""

    def get_parser(self, prog_name):
        parser = super(UseGroupCommand, self).get_parser(prog_name)
        parser.add_argument(
            'group', metavar='GROUP_ID or GROUP_NAME',
            help='This group name will be used as default group.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Use Group.')


class SshIdentityCommand(DetailCommand):

    """Operate with ssh identity object."""

    def get_parser(self, prog_name):
        parser = super(SshIdentityCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for host.'
        )
        parser.add_argument(
            '-u', '--username',
            metavar='USERNAME', help="Username of host's user."
        )
        parser.add_argument(
            '-p', '--password',
            metavar='PASSWORD', help="Password of Host's user."
        )
        parser.add_argument(
            '-i', '--identity-file',
            metavar='PRIVATE_KEY', help="Private key."
        )
        parser.add_argument(
            '-k', '--ssh-key',
            metavar='SSH_KEY', help="Serveraduitor's ssh key's name or id."
        )
        parser.add_argument(
            'ssh_identity', nargs='*', metavar='IDENITY_ID or IDENITY_NAME',
            help='Pass to edit exited identities.'
        )
        return parser

    def create_identity(self, parsed_args):
        if parsed_args.generate_key:
            raise NotImplementedError('Not implemented')

        if parsed_args.identity_file:
            raise NotImplementedError('Not implemented')

        if parsed_args.ssh_key:
            raise NotImplementedError('Not implemented')

        identity = SshIdentity()
        identity.username = parsed_args.username
        identity.password = parsed_args.password

        with self.storage:
            saved_host = self.storage.save(identity)
        return saved_host

    def take_action(self, parsed_args):
        if not parsed_args.ssh_identities:
            ssh_identity = self.create_identity(parsed_args)
            self.log.info('%s', ssh_identity.id)
        else:
            self.log.info('SshIdentity object.')


class SshIdentitiesCommand(ListCommand):

    """Manage ssh identity objects."""

    def take_action(self, parsed_args):
        ssh_identities = self.storage.get_all(SshIdentity)
        fields = SshIdentity.allowed_feilds()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in ssh_identities]


class SshConfigArgs(object):

    def add_agrs(self, parser):
        parser.add_argument(
            '-p', '--port',
            type=int, metavar='PORT',
            help='Ssh port.'
        )
        parser.add_argument(
            '-S', '--strict-key-check', action='store_true',
            help='Provide to force check ssh server public key.'
        )
        parser.add_argument(
            '-s', '--snippet', metavar='SNIPPET_ID or SNIPPET_NAME',
            help='Snippet id or snippet name.'
        )
        parser.add_argument(
            '--ssh-identity',
            metavar='SSH_IDENTITY', help="Ssh identity's id name or name."
        )
        parser.add_argument(
            '-k', '--keep-alive-packages',
            type=int, metavar='PACKAGES_COUNT',
            help='ServerAliveCountMax option from ssh_config.'
        )
        parser.add_argument(
            '-u', '--username', metavar='SSH_USERNAME',
            help='Username for authenticate to ssh server.'
        )
        parser.add_argument(
            '-P', '--password', metavar='SSH_PASSWORD',
            help='Password for authenticate to ssh server.'
        )
        parser.add_argument(
            '-i', '--identity-file', metavar='IDENTITY_FILE',
            help=('Selects a file from which the identity (private key) '
                  'for public key authentication is read.')
        )
        parser.add_argument(
            'command', nargs='?', metavar='COMMAND',
            help='Create and assign automatically snippet.'
        )
        return parser


class HostCommand(DetailCommand):

    """Operate with Host object."""

    def get_parser(self, prog_name):
        parser = super(HostCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for host.'
        )
        parser.add_argument(
            '--ssh', metavar='SSH_CONFIG_OPTIONS',
            help='Options in ssh_config format.'
        )
        parser.add_argument(
            '-t', '--tags', metavar='TAG_LIST',
            help='Comma separated tag list for host, e.g. "web,django".'
        )
        parser.add_argument(
            '-g', '--group', metavar='GROUP_ID or GROUP_NAME',
            help='Move hosts to this group.'
        )
        parser.add_argument(
            '-a', '--address',
            metavar='ADDRESS', help='Address of host.'
        )
        parser.add_argument(
            'host', nargs='*', metavar='HOST_ID or HOST_NAME',
            help='Pass to edit exited hosts.'
        )

        ssh_config_args = SshConfigArgs()
        ssh_config_args.add_agrs(parser)
        return parser

    def create_host(self, parsed_args):
        if parsed_args.generate_key:
            raise NotImplementedError('Not implemented')

        if parsed_args.group:
            raise NotImplementedError('Not implemented')

        if parsed_args.ssh_identity:
            raise NotImplementedError('Not implemented')

        identity = SshIdentity()
        identity.username = parsed_args.username
        identity.password = parsed_args.password

        config = SshConfig()
        config.port = parsed_args.port
        config.ssh_identity = identity

        host = Host()
        host.label = parsed_args.label
        host.address = parsed_args.address
        host.ssh_config = config

        with self.storage:
            saved_host = self.storage.save(host)
        return saved_host

    def take_action(self, parsed_args):
        if not parsed_args.host:
            host = self.create_host(parsed_args)
            self.log.info('%s', host.id)
        else:
            self.log.info('Host object.')


class HostsCommand(ListCommand):

    """Manage host objects."""

    def get_parser(self, prog_name):
        parser = super(HostsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-t', '--tags', metavar='TAG_LIST',
            help=('(Comma separated tag list) list hosts with such tags.')
        )
        parser.add_argument(
            '-g', '--group', metavar='GROUP_ID or GROUP_NAME',
            help=('List hosts in group (default is current group).')
        )
        return parser

    def take_action(self, parsed_args):
        hosts = self.storage.get_all(Host)
        fields = Host.allowed_feilds()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in hosts]


class GroupCommand(DetailCommand):

    """Operate with Group object."""

    def get_parser(self, prog_name):
        parser = super(GroupCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for group.'
        )
        parser.add_argument(
            '--ssh', help='Options in ssh_config format.'
        )
        parser.add_argument(
            '-g', '--parent-group',
            metavar='PARENT_GROU', help="Parent group's id or name."
        )
        parser.add_argument(
            'group', nargs='*', metavar='GROUP_ID or GROUP_NAME',
            help='Pass to edit exited groups.'
        )

        ssh_config_args = SshConfigArgs()
        ssh_config_args.add_agrs(parser)
        return parser

    def create_group(self, parsed_args):
        if parsed_args.generate_key:
            raise NotImplementedError('Not implemented')
        if parsed_args.parent_group:
            raise NotImplementedError('Not implemented')
        if parsed_args.ssh_identity:
            raise NotImplementedError('Not implemented')

        identity = SshIdentity()
        identity.username = parsed_args.username
        identity.password = parsed_args.password

        config = SshConfig()
        config.port = parsed_args.port
        config.ssh_identity = identity

        group = Group()
        group.label = parsed_args.label
        group.ssh_config = config

        with self.storage:
            saved_host = self.storage.save(group)
        return saved_host

    def take_action(self, parsed_args):
        if not parsed_args.group:
            group = self.create_group(parsed_args)
            self.log.info('%s', group.id)
        else:
            self.log.info('Host object.')


class GroupsCommand(ListCommand):

    """Manage group objects."""

    def get_parser(self, prog_name):
        parser = super(GroupsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-r', '--recursive', action='store_true',
            help=('List groups of current group '
                  '(default is current group) recursively.')
        )
        parser.add_argument(
            'group', nargs='?', metavar='GROUP_ID or GROUP_NAME',
            help='List groups in this group.'
        )
        return parser

    def take_action(self, parsed_args):
        groups = self.storage.get_all(Group)
        fields = Group.allowed_feilds()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in groups]


class InvalidBinging(Exception):
    pass


class BindingParser(object):

    local_pf_re = re.compile(
        r'^((?P<bound_address>\S+):)?(?P<local_port>\d+)'
        r':(?P<hostname>\S+):(?P<remote_port>\d+)$'
    )
    dynamic_pf_re = re.compile(
        r'^((?P<bound_address>\S+):)?(?P<local_port>\d+)'
        r'(?P<hostname>)(?P<remote_port>)$'
        # Regexp Groups should be the same for all rules.
    )

    @classmethod
    def parse(cls, regexp, binding_str):
        matched = regexp.match(binding_str)
        if not matched:
            raise InvalidBinging('Invalid binding format.')
        return matched.groupdict()

    @classmethod
    def local(cls, binding_str):
        return cls.parse(cls.local_pf_re, binding_str)

    @classmethod
    def dynamic(cls, binding_str):
        return cls.parse(cls.dynamic_pf_re, binding_str)


class PFRuleCommand(DetailCommand):

    """Operate with port forwarding rule object."""

    binding_parsers = {
        'D': BindingParser.dynamic,
        'L': BindingParser.local,
    }
    binding_parsers['R'] = binding_parsers['L']

    def get_parser(self, prog_name):
        parser = super(PFRuleCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-H', '--host', metavar='HOST_ID or HOST_NAME',
            help='Create port forwarding rule for this host.'
        )
        parser.add_argument(
            '--dynamic', dest='type', action='store_const',
            const='D', help='Dynamic port forwarding.'
        )
        parser.add_argument(
            '--remote', dest='type', action='store_const',
            const='R', help='Remote port forwarding.'
        )
        parser.add_argument(
            '--local', dest='type', action='store_const',
            const='L', help='Local port forwarding.'
        )
        parser.add_argument(
            'binding', metavar='BINDINDS',
            help=('Specify binding of ports and addresses '
                  '[bind_address:]port or [bind_address:]port:host:hostport')
        )
        parser.add_argument(
            'pr-rule', nargs='?', metavar='PF_RULE_ID or PF_RULE_NAME',
            help='Pass to edit exited port Frowarding Rule.'
        )
        return parser

    def parse_binding(self, pf_type, binding):
        return self.binding_parsers[pf_type](binding)

    def create_pfrule(self, parsed_args):
        if not parsed_args.host:
            raise ValueError('Host is required.')
        else:
            raise NotImplementedError('Not implimented now.')

        pf_rule = PFRule()
        pf_rule.pf_type = parsed_args.type
        binding_dict = self.parse_binding(pf_rule.pf_type, parsed_args.binging)
        for k, v in binding_dict.items():
            setattr(pf_rule, k, v)

        with self.storage:
            saved_pfrule = self.storage.save(pf_rule)
        return saved_pfrule

    def take_action(self, parsed_args):
        if not parsed_args.pr_rule:
            pfrule = self.create_pfrule(parsed_args)
            self.log.info('%s', pfrule.id)
        else:
            self.log.info('Host object.')

class PFRulesCommand(ListCommand):

    """Manage port forwarding rule objects."""

    def take_action(self, parsed_args):
        pf_rules = self.storage.get_all(PFRule)
        fields = PFRule.allowed_feilds()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in pf_rules]


class TagsCommand(ListCommand):

    """Manage tag objects."""

    def get_parser(self, prog_name):
        parser = super(TagsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='Delete tags.'
        )
        parser.add_argument(
            'tags', nargs='+', metavar='TAG_ID or TAG_NAME',
            help="List infos about this tags."
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Tag objects.')


class InfoCommand(AbstractCommand):

    """Show info about host or group."""

    def get_parser(self, prog_name):
        parser = super(InfoCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-G', '--group', dest='entry_type',
            action='store_const', const='group',
            help='Show info about group.'
        )
        parser.add_argument(
            '-H', '--host', dest='entry_type',
            action='store_const', const='host',
            help='Show info about host.'
        )
        parser.add_argument(
            '-M', '--no-merge', action='store_true',
            help='Do not merge configs.'
        )
        parser.add_argument(
            '--ssh', action='store_true',
            help='Show info in ssh_config format'
        )
        parser.add_argument('id_or_name', metavar='ID or NAME')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Info about group or host.')
