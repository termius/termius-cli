# -*- coding: utf-8 -*-
"""Module for tag command."""
from ..core.commands import ListCommand
from ..core.commands.mixins import InstanceOperationMixin, GetObjectsMixin
from ..core.models.terminal import Tag


class TagsCommand(GetObjectsMixin, InstanceOperationMixin, ListCommand):
    """list all tags"""

    model_class = Tag

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='delete the selected tags'
        )
        parser.add_argument(
            'tags', nargs='*', metavar='ID or NAME',
            help='select the tag with ID or NAME and list info'
        )
        return parser

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        if parsed_args.tags:
            tags = self.get_objects(parsed_args.tags)
        else:
            tags = self.storage.get_all(Tag)
        if parsed_args.delete:
            for i in tags:
                self.delete_instance(i)
        return self.prepare_result(tags)
