from operator import attrgetter
from ...core.commands import ListCommand, DetailCommand
from ..models import Snippet


class SnippetCommand(DetailCommand):

    """Operate with Group object."""

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

    def create_snippet(self, parsed_args):
        if not parsed_args.script:
            raise ArgumentRequiredException('Script is required')

        snippet = Snippet()
        snippet.script = parsed_args.script
        snippet.label = parsed_args.label

        with self.storage:
            saved_snippet = self.storage.save(snippet)
        return saved_snippet

    def take_action(self, parsed_args):
        if not parsed_args.snippet:
            snippet = self.create_snippet(parsed_args)
            self.app.stdout.write('{}\n'.format(snippet.id))
        else:
            self.log.info('Snippet object.')


class SnippetsCommand(ListCommand):

    """Manage snippet objects."""

    def take_action(self, parsed_args):
        groups = self.storage.get_all(Snippet)
        fields = Snippet.allowed_feilds()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in groups]
