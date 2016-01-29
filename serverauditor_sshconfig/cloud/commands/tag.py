# -*- coding: utf-8 -*-
"""Module for tag command."""
from ...core.commands import ListCommand
from ...core.commands.mixins import GetObjectsMixin
from ..models import Tag


class TagsCommand(GetObjectsMixin, ListCommand):
    """Manage tag objects."""

    model_class = Tag

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
        tags = self.get_objects(parsed_args.tags)
        return self.prepare_result(tags)
