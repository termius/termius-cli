from ...core.commands import ListCommand


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
