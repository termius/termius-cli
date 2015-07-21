# coding: utf-8
from .core.commands import AbstractCommand



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
        return parser


class HostCommand(AbstractCommand):

    """Operate with Host object."""

    def get_parser(self, prog_name):
        parser = super(HostCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='Delete hosts.'
        )
        parser.add_argument(
            '-I', '--interactive', action='store_true',
            help='Enter to interactive mode.'
        )
        parser.add_argument(
            '-L', '--label', metavar='NAME',
            help="Alias and Host's label in Serverauditor"
        )
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for host.'
        )
        parser.add_argument(
            '--ssh', metavar='SSH_CONFIG_OPTIONS',
            help='Options in ssh_config format.'
        )
        parser.add_argument(
            '-t', '--tags',  metavar='TAG_LIST',
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
            'host',  nargs='*', metavar='HOST_ID or HOST_NAME',
            help='Pass to edit exited hosts.'
        )
        parser.add_argument(
            'command', nargs='?', metavar='COMMAND',
            help='Create and assign automatically snippet.'
        )

        ssh_config_args = SshConfigArgs()
        ssh_config_args.add_agrs(parser)
        return parser

    def take_action(self, parsed_args):
        self.log.info('Host object.')


class HostsCommand(AbstractCommand):

    """Manage host objects."""

    def get_parser(self, prog_name):
        parser = super(HostsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-l', '--list', action='store_true',
            help=('List hosts in current group with id, name, group in path '
                  'format, tags, username, address and port.')
        )
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
        self.log.info('Host objects.')


class GroupCommand(AbstractCommand):

    """Operate with Group object."""

    def get_parser(self, prog_name):
        parser = super(GroupCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='Delete groups.'
        )
        parser.add_argument(
            '-I', '--interactive', action='store_true',
            help='Enter to interactive mode.'
        )
        parser.add_argument(
            '-L', '--label', metavar='NAME',
            help="Group' label in Serverauditor"
        )
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for group.'
        )
        parser.add_argument(
            '--ssh', help='Options in ssh_config format.'
        )
        parser.add_argument(
            'group',  nargs='*', metavar='GROUP_ID or GROUP_NAME',
            help='Pass to edit exited groups.'
        )

        ssh_config_args = SshConfigArgs()
        ssh_config_args.add_agrs(parser)
        return parser

    def take_action(self, parsed_args):
        self.log.info('Group object.')


class GroupsCommand(AbstractCommand):

    """Manage group objects."""

    def get_parser(self, prog_name):
        parser = super(GroupsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-l', '--list', action='store_true',
            help=('List groups of group (default is current group) with '
                  'id, name, parent group in path format, username and port.')
        )
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
        self.log.info('Group objects.')


class PFRuleCommand(AbstractCommand):

    """Operate with port forwarding rule object."""

    def get_parser(self, prog_name):
        parser = super(PFRuleCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='Delete hosts.'
        )
        parser.add_argument(
            '-I', '--interactive', action='store_true',
            help='Enter to interactive mode.'
        )
        parser.add_argument(
            '-L', '--label',  metavar='NAME',
            help="Port frowarding rule' label in Serverauditor"
        )
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

    def take_action(self, parsed_args):
        self.log.info('Port Forwarding Rule object.')


class PFRulesCommand(AbstractCommand):

    """Manage port forwarding rule objects."""

    def get_parser(self, prog_name):
        parser = super(PFRulesCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-l', '--list', action='store_true',
            help=("List port frowarding rules with "
                  "id, name, host's name, host' group in path format, "
                  "type and dinding.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Port Forwarding Rule objects.')


class TagsCommand(AbstractCommand):

    """Manage tag objects."""

    def get_parser(self, prog_name):
        parser = super(TagsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='Delete tags.'
        )
        parser.add_argument(
            '-l', '--list', action='store_true',
            help="List tags ids, name, and host's ids with such tag"
        )
        parser.add_argument(
            'tags', nargs='+', metavar='TAG_ID or TAG_NAME',
            help="List infos about this tags."
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Tag objects.')


class PushCommand(AbstractCommand):

    """Push data to Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PushCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--silent', action='store_true',
            help='Do not produce any interactions.'
        )
        parser.add_argument(
            '-S', '--strategy', metavar='STRATEGY_NAME',
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
            '-s', '--silent', action='store_true',
            help='Do not produce any interactions.'
        )
        parser.add_argument(
            '-S', '--strategy', metavar='STRATEGY_NAME',
            help='Force to use specific strategy to merge data.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Pull data from Serverauditor cloud.')


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


class ConnectCommand(AbstractCommand):

    """Connect to specific host."""

    def get_parser(self, prog_name):
        parser = super(ConnectCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-G', '--group', metavar='GROUP_ID or GROUP_NAME',
            help=("Use this group's (default is active group) config "
                  "to merge with host's config.")
        )
        parser.add_argument(
            '--ssh', metavar='SSH_CONFIG_OPTIONS',
            help='Options in ssh_config format.'
        )
        parser.add_argument(
            'host', metavar='HOST_ID or HOST_NAME',
            help='Connect to this host.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Connect to host %s.', parsed_args['host'])
