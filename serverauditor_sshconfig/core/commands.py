# coding: utf-8
import logging

from cliff.command import Command
from cliff.lister import Lister


class AbstractCommand(Command):

    "Abstract Command with log."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AbstractCommand, self).get_parser(prog_name)
        parser.add_argument('--log-file', help="Path to log file.")
        return parser


class DetailCommand(AbstractCommand):

    def get_parser(self, prog_name):
        parser = super(DetailCommand, self).get_parser(prog_name)
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
        return parser


class ListCommand(Lister):

    def get_parser(self, prog_name):
        parser = super(ListCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-l', '--list', action='store_true',
            help=('List hosts in current group with id, name, group in path '
                  'format, tags, username, address and port.')
        )
        parser.add_argument('--log-file', help="Path to log file.")
        return parser
