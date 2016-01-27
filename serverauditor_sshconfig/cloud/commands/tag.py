# -*- coding: utf-8 -*-
"""Module for tag command."""
from ...core.commands import ListCommand


class TagsCommand(ListCommand):
    """Manage tag objects."""

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(TagsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='Delete tags.'
        )
        parser.add_argument(
            'tags', nargs='+', metavar='TAG_ID or TAG_NAME',
            help='List infos about this tags.'
        )
        return parser

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        self.log.info('Tag objects.')
        assert False, 'Not implemented'
