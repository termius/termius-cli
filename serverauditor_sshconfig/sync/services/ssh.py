# -*- coding: utf-8 -*-
"""Module with ssh services."""
from .base import BaseSyncService


class SSHService(BaseSyncService):
    """Synchronize ssh config content with application."""

    def hosts(self):
        """Retrieve host instances from ssh config."""
        return []
