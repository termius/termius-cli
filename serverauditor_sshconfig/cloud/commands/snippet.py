from operator import attrgetter
from ...core.commands import ListCommand, DetailCommand
from ..models import Snippet


class SnippetCommand(DetailCommand):

    """Operate with Group object."""

    allowed_operations = DetailCommand.all_operations

    def get_parser(self, prog_name):
        parser = super(SnippetCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--script', metavar='SCRIPT',
            help='Shell Script for snippet.'
        )
        parser.add_argument(
            'snippet', nargs='?', metavar='SNIPPET_ID or SNIPPET_NAME',
            help='Pass to edit exited snippets.'
        )
        return parser

    def create(self, parsed_args):
        if not parsed_args.script:
            raise ArgumentRequiredException('Script is required')

        snippet = Snippet()
        snippet.script = parsed_args.script
        snippet.label = parsed_args.label

        with self.storage:
            saved_snippet = self.storage.save(snippet)
        self.log_create(saved_snippet)


class SnippetsCommand(ListCommand):

    """Manage snippet objects."""

    def take_action(self, parsed_args):
        groups = self.storage.get_all(Snippet)
        fields = Snippet.allowed_fields()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in groups]
