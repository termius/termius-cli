# -*- coding: utf-8 -*-
from unittest import TestCase

import six
from mock import patch, Mock

from termius.core.models.base import Model
from termius.core.models.terminal import (
    Tag, SshKey, Identity, SshConfig, Group, Host, PFRule
)

from termius.core.storage import ApplicationStorage


class ModelsTest(TestCase):
    def test_generator(self):
        model_classes = (
            Host, Group, Tag,
            SshKey, Identity, SshConfig,
            Group, Host, PFRule
        )
        for model_class in model_classes:
            instance = model_class()
            not_fk_field_names = (
                k for k, v in instance.fields.items()
                if not issubclass(v.model, Model)
            )
            for i in not_fk_field_names:
                setattr(instance, i, i)

            yield self.save, instance

    @patch('termius.core.storage.PersistentDict')
    def save(self, model, mocked):

        storage = ApplicationStorage(Mock(**{
            'app.directory_path.return_value': 'TestCase'
        }))
        with storage:
            saved_model = storage.save(model)

        assert isinstance(saved_model.id, six.integer_types)

        fk_field_names = (
            k for k, v in saved_model.fields.items()
            if issubclass(v.model, Model)
        )
        for i in fk_field_names:
            setattr(model, i, None)
        stored_models = [saved_model]

        driver = mocked.return_value
        driver.__setitem__.assert_called_with(model.set_name, stored_models)
        driver.sync.assert_called_with()
