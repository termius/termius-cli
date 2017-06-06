# -*- coding: utf-8 -*-
"""Module with logic for Analytics."""

import platform

from google_measurement_protocol import Event, report

from termius.account.managers import AccountManager
from termius.core.settings import Config
from termius import __version__


class Analytics(object):
    """Class to send Analytics."""

    def __init__(self, app, config=None):
        """Construct new Analytics instance."""
        self.config = config
        self.app = app

        if self.config is None:
            self.config = Config(self)

        self.manager = AccountManager(self.config)

    def send_analytics(self, cmd_name):
        """Send event to google analytics."""
        os_info = '%s %s' % (platform.system(), platform.release())

        info = [
            {'av': __version__},
            {'an': 'Termius CLI'},
            {'ua': os_info},
            {'ostype': os_info}
        ]

        event = Event('cli', cmd_name)
        report(
            self.tracking_id,
            self.manager.analytics_id,
            event,
            extra_info=info
        )

    @property
    def tracking_id(self):
        """Google Analytics id for termius cli application."""
        return 'UA-56746272-4'
