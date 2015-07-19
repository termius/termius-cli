# coding: utf-8
import logging

from cliff.command import Command


class AbstractCommand(Command):

    "Abstract Command with log."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AbstractCommand, self).get_parser(prog_name)
        parser.add_argument('--log-file')
        return parser


class SyncCommand(AbstractCommand):

    """Sync with IaaS or PaaS."""

    def get_parser(self, prog_name):
        parser = super(SyncCommand, self).get_parser(prog_name)
        parser.add_argument('-c', '--credentials')
        parser.add_argument('service', metavar='SERVICE')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Sync with service {}.'.format(parsed_args['service']))


class UseGroupCommand(AbstractCommand):

    """Change group."""

    def get_parser(self, prog_name):
        parser = super(UseGroupCommand, self).get_parser(prog_name)
        parser.add_argument('group', metavar='GROUP_ID or GROUP_NAME')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Use Group.')


class SshConfigArgs(object):

    def add_agrs(self, parser):
        parser.add_argument('-p', '--port', type=int, metavar='PORT')
        parser.add_argument('-S', '--strict-key-check', action='store_true')
        parser.add_argument(
            '-s', '--snippet', metavar='SNIPPET_ID or SNIPPET_NAME'
        )
        parser.add_argument(
            '-k', '--keep-alive-packages', type=int, metavar='PACKAGES_COUNT'
        )
        parser.add_argument(
            '-u', '--username', metavar='SSH_USERNAME'
        )
        parser.add_argument(
            '-P', '--password', metavar='SSH_PASSWORD'
        )
        parser.add_argument(
            '-i', '--identity-file', metavar='IDENTITY_FILE'
        )
        return parser


class HostCommand(AbstractCommand):

    """Operate with Host object."""

    def get_parser(self, prog_name):
        parser = super(HostCommand, self).get_parser(prog_name)
        parser.add_argument('-d', '--delete', action='store_true')
        parser.add_argument('--generate-key', action='store_true')
        parser.add_argument('-I', '--interactive', action='store_true')
        parser.add_argument('--ssh')
        parser.add_argument('-t', '--tags',  metavar='TAG_LIST')
        parser.add_argument('-g', '--group',  metavar='GROUP_ID or GROUP_NAME')
        parser.add_argument('-a', '--address',  metavar='ADDRESS')
        parser.add_argument('-L', '--label',  metavar='NAME')
        parser.add_argument(
            'host',  nargs='*', metavar='HOST_ID or HOST_NAME'
        )
        parser.add_argument('command', nargs='?', metavar='COMMAND')

        ssh_config_args = SshConfigArgs()
        ssh_config_args.add_agrs(parser)
        return parser

    def take_action(self, parsed_args):
        self.log.info('Host object.')


class HostsCommand(AbstractCommand):

    """Manage host objects."""

    def get_parser(self, prog_name):
        parser = super(HostsCommand, self).get_parser(prog_name)
        parser.add_argument('-l', '--list', action='store_true')
        parser.add_argument('-t', '--tags', metavar='TAG_LIST')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Host objects.')


class GroupCommand(AbstractCommand):

    """Operate with Group object."""

    def get_parser(self, prog_name):
        parser = super(GroupCommand, self).get_parser(prog_name)
        parser.add_argument('-d', '--delete', action='store_true')
        parser.add_argument('--generate-key', action='store_true')
        parser.add_argument('-I', '--interactive', action='store_true')
        parser.add_argument('--ssh', metavar='COMMAND')
        parser.add_argument(
            '-L', '--label',  metavar='NAME'
        )
        parser.add_argument(
            'group',  nargs='*', metavar='GROUP_ID or GROUP_NAME'
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
        parser.add_argument('-l', '--list', action='store_true')
        parser.add_argument('-r', '--recursive')
        parser.add_argument(
            'group', nargs='?', metavar='GROUP_ID or GROUP_NAME'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Group objects.')


class PFRuleCommand(AbstractCommand):

    """Operate with port forwarding rule object."""

    def get_parser(self, prog_name):
        parser = super(PFRuleCommand, self).get_parser(prog_name)
        parser.add_argument('-d', '--delete', action='store_true')
        parser.add_argument('-H', '--host', nargs=1, metavar='HOST_ID or HOST_NAME')
        parser.add_argument('-I', '--interactive', action='store_true')
        parser.add_argument('--dynamic',  action='store_true')
        parser.add_argument('--remote',  action='store_true')
        parser.add_argument('--local',  action='store_true')
        parser.add_argument('-L', '--label',  metavar='NAME')
        parser.add_argument('command', metavar='bind_address:port:host:hostport or port:host:hostport')
        parser.add_argument(
            'pr-rule', nargs='?', metavar='PF_RULE_ID or PF_RULE_NAME'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Port Forwarding Rule object.')


class PFRulesCommand(AbstractCommand):

    """Manage port forwarding rule objects."""

    def get_parser(self, prog_name):
        parser = super(PFRulesCommand, self).get_parser(prog_name)
        parser.add_argument('-l', '--list', action='store_true')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Port Forwarding Rule objects.')


class TagsCommand(AbstractCommand):

    """Manage tag objects."""

    def get_parser(self, prog_name):
        parser = super(TagsCommand, self).get_parser(prog_name)
        parser.add_argument('-d', '--delete', action='store_true')
        parser.add_argument('-l', '--list', action='store_true')
        parser.add_argument('tags', nargs='+', metavar='TAG_ID or TAG_NAME')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Tag objects.')


class LoginCommand(AbstractCommand):

    """Sign into serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(LoginCommand, self).get_parser(prog_name)
        parser.add_argument('-u', '--username', metavar='USERNAME')
        parser.add_argument('--sync-sshconfig', action='store_true')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Sign into serverauditor cloud.')


class LogoutCommand(AbstractCommand):

    """Sign out serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(LogoutCommand, self).get_parser(prog_name)
        parser.add_argument('--clear-sshconfig', action='store_true')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Sign out serverauditor cloud.')


class PushCommand(AbstractCommand):

    """Push data to Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PushCommand, self).get_parser(prog_name)
        parser.add_argument('-s', '--silent', action='store_true')
        parser.add_argument('-S', '--strategy', metavar='STRATEGY_NAME')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Push data to Serverauditor cloud.')


class PullCommand(AbstractCommand):

    """Pull data from Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PullCommand, self).get_parser(prog_name)
        parser.add_argument('-s', '--silent', action='store_true')
        parser.add_argument('-S', '--strategy', metavar='STRATEGY_NAME')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Pull data from Serverauditor cloud.')


class InfoCommand(AbstractCommand):

    """Show info about host or group."""

    def get_parser(self, prog_name):
        parser = super(InfoCommand, self).get_parser(prog_name)
        parser.add_argument('-G', '--group', metavar='GROUP_ID or GROUP_NAME')
        parser.add_argument('-H', '--host', metavar='HOST_ID or HOST_NAME')
        parser.add_argument('--ssh', action='store_true')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Info about group or host.')


class ConnectCommand(AbstractCommand):

    """Connect to specific host."""

    def get_parser(self, prog_name):
        parser = super(ConnectCommand, self).get_parser(prog_name)
        parser.add_argument('-G', '--group', metavar='GROUP_ID or GROUP_NAME')
        parser.add_argument('--ssh', metavar='SSH_CONFIG_OPTIONS')
        parser.add_argument('host', metavar='HOST_ID or HOST_NAME')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Connect to host {}.'.format(parsed_args['host']))
