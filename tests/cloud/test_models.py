import six
from collections import OrderedDict
from mock import patch, Mock
from serverauditor_sshconfig.cloud.models import (
    Host, Group, Tag, SshKey, SshIdentity, SshConfig, Group, Host, PFRule
)

from serverauditor_sshconfig.core.settings import ApplicationStorage


def test_generator():
    model_classes = (
        Host, Group, Tag,
        SshKey, SshIdentity, SshConfig,
        Group, Host, PFRule
    )
    for model_class in model_classes:
        instance = model_class()
        not_fk_instance = (i for i in instance.fields if i not in instance.mapping)
        for i in not_fk_instance:
            setattr(instance, i, i)

        yield save, instance


@patch('serverauditor_sshconfig.core.settings.PersistentDict')
def save(model, mocked):

    storage = ApplicationStorage('test')
    storage.save(model)

    assert isinstance(model.id, six.integer_types)

    for k, v in model.mapping.items():
        setattr(model, k, [] if v.many else None)
    stored_models = OrderedDict(((model.id, model),))

    driver = mocked.return_value
    driver.__setitem__.assert_called_with(model.set_name, stored_models)
    driver.sync.assert_called_with()
