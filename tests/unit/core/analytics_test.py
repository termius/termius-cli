from unittest import TestCase

import mock as mock
from six.moves import configparser

from termius.app import TermiusApp
from termius.core.analytics import Analytics


class TestAnalytics(TestCase):
    def setUp(self):
        self.app = TermiusApp()

        self.config_patch = mock.patch('termius.core.analytics.Config')
        self.config_class = self.config_patch.start()
        self.config = mock.Mock()
        self.config_class.return_value = self.config

    def tearDown(self):
        self.config_patch.stop()

    def test_get_client_id(self):
        client_id = 'client'

        self.config.get.return_value = client_id

        analytics = Analytics(self.app)
        result = analytics.get_client_id()

        self.assertEquals(result, client_id)
        self.config_class.assert_called_once_with(analytics)
        self.config.get.assert_called_once_with('User', 'username')



    @mock.patch('termius.core.analytics.uuid')
    def test_get_client_id_when_not_logged(self, uuid):
        random_id = 'uuid'
        uuid.uuid4.return_value = random_id

        self.config.get.side_effect = configparser.NoSectionError('msg')

        analytics = Analytics(self.app)
        result = analytics.get_client_id()

        self.assertEquals(result, random_id)
        self.config_class.assert_called_once_with(analytics)
        self.config.get.assert_called_once_with('User', 'username')
        uuid.uuid4.assert_called_once()

    @mock.patch('termius.core.analytics.report')
    @mock.patch('termius.core.analytics.Analytics.get_client_id')
    @mock.patch('termius.core.analytics.Event')
    def test_send_analytics(self, event_class, get_client_id, report):
        cmd_name = 'command'
        client_id = 'client'

        event = mock.Mock()
        event_class.return_value = event
        get_client_id.return_value = client_id

        analytics = Analytics(self.app)
        analytics.send_analytics(cmd_name)

        event_class.assert_called_once_with('cli', cmd_name)
        report.assert_called_once_with(
            analytics.tracking_id, client_id, event
        )
