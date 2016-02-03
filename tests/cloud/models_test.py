# -*- coding: utf-8 -*-
import six
from mock import patch

from serverauditor_sshconfig.core.models.base import Model
from serverauditor_sshconfig.core.models.terminal import (
    Host, Group, Tag, SshKey, SshIdentity, SshConfig, Group, Host, PFRule
)

from serverauditor_sshconfig.core.storage import ApplicationStorage


def test_generator():
    model_classes = (
        Host, Group, Tag,
        SshKey, SshIdentity, SshConfig,
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

        yield save, instance


@patch('serverauditor_sshconfig.core.storage.PersistentDict')
def save(model, mocked):

    storage = ApplicationStorage('test')
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
