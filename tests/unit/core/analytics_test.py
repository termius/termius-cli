from unittest import TestCase

import mock as mock
import platform
from six.moves import configparser

from termius import __version__
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

    @mock.patch('termius.core.analytics.report')
    @mock.patch(
        'termius.core.analytics.AccountManager.analytics_id',
        new_callable=mock.PropertyMock
    )
    @mock.patch('termius.core.analytics.Event')
    def test_send_analytics(self, event_class, analytics_id, report):
        cmd_name = 'command'
        client_id = 'client'

        os = '%s %s' % (platform.system(), platform.release())

        info = [
            {'av': __version__},
            {'an': 'Termius CLI'},
            {'ua': os},
            {'ostype': os}
        ]

        event = mock.Mock()
        event_class.return_value = event
        analytics_id.return_value = client_id

        analytics = Analytics(self.app)
        analytics.send_analytics(cmd_name)

        analytics_id.assert_called_once_with()
        event_class.assert_called_once_with('cli', cmd_name)
        report.assert_called_once_with(
            analytics.tracking_id, client_id, event, extra_info=info
        )
