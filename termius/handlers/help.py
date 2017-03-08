# -*- coding: utf-8 -*-
"""Module with Help command."""

from cliff.help import HelpCommand as BaseHelpCommand

from termius.core.analytics import Analytics


class HelpCommand(BaseHelpCommand):
    """Help command overridden to collect analytics."""

    def run(self, parsed_args):
        """Overridden to collect analytics."""
        analytics = Analytics(self.app)
        analytics.send_analytics(self.cmd_name)

        return super(HelpCommand, self).run(parsed_args)
