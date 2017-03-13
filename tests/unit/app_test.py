from unittest import TestCase

import mock

from termius.app import TermiusApp
from termius.handlers import HostCommand


class TestApp(TestCase):
    def setUp(self):
        self.app = TermiusApp()

    @mock.patch('termius.app.os.getenv')
    @mock.patch('termius.app.Analytics')
    def test_prepare_to_run_with_analytics(self, analytics_class, getenv):
        analytics = mock.Mock()
        analytics_class.return_value = analytics
        getenv.return_value = None

        cmd_name = 'command'
        command = HostCommand(self.app, None, cmd_name)

        self.app.prepare_to_run_command(command)

        getenv.assert_called_once_with('NOT_COLLECT_STAT')
        analytics_class.assert_called_once_with(self.app, command.config)
        analytics.send_analytics.assert_called_once_with(cmd_name)

    @mock.patch('termius.app.os.getenv')
    @mock.patch('termius.app.TermiusApp.collect_analytics')
    def test_prepare_to_run_without_analytics(self, collect_analytics, getenv):
        getenv.return_value = True
        command = HostCommand(self.app, None, 'command')

        self.app.prepare_to_run_command(command)

        getenv.assert_called_once_with('NOT_COLLECT_STAT')
        collect_analytics.assert_not_called()


