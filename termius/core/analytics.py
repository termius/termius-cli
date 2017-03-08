# -*- coding: utf-8 -*-
"""Module with logic for Analytics."""

import uuid

from google_measurement_protocol import Event, report
from six.moves import configparser

from termius.core.settings import Config


class Analytics(object):
    """Class to send Analytics."""

    def __init__(self, app, config=None):
        """Construct new Analytics instance."""
        self.config = config
        self.app = app

        if self.config is None:
            self.config = Config(self)

    def get_client_id(self):
        """Get user`s email or generate random id."""
        try:
            client_id = self.config.get('User', 'username')
        except configparser.NoSectionError:
            client_id = uuid.uuid4()

        return client_id

    def send_analytics(self, cmd_name):
        """Send event to google analytics."""
        event = Event('cli', cmd_name)
        client_id = self.get_client_id()

        report(self.tracking_id, client_id, event)

    @property
    def tracking_id(self):
        """Google Analytics id for termius cli application."""
        return 'UA-56746272-3'
