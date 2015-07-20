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
