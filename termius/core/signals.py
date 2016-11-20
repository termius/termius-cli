# -*- coding: utf-8 -*-
"""Package with application signals."""
from blinker import signal


# pylint: disable=invalid-name
pre_create_instance = signal('pre-create-instance')
# pylint: disable=invalid-name
post_create_instance = signal('post-create-instance')

# pylint: disable=invalid-name
pre_update_instance = signal('pre-update-instance')
# pylint: disable=invalid-name
post_update_instance = signal('post-update-instance')

# pylint: disable=invalid-name
pre_delete_instance = signal('pre-delete-instance')
# pylint: disable=invalid-name
post_delete_instance = signal('post-delete-instance')

# pylint: disable=invalid-name
post_logout = signal('post_logout')
