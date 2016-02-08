# -*- coding: utf-8 -*-
from blinker import signal


pre_create_instance = signal('pre-create-instance')
post_create_instance = signal('post-create-instance')

pre_update_instance = signal('pre-update-instance')
post_update_instance = signal('post-update-instance')

pre_delete_instance = signal('pre-delete-instance')
post_delete_instance = signal('post-delete-instance')
