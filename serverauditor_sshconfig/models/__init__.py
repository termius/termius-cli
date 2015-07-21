from ..core.models import Model, Mapping


class Tag(Model):

    fields = {'label'}
    set_name = 'tag_set'


class SshKey(Model):

    fields = {'label', 'passphrase', 'private_key', 'public_key'}
    set_name = 'sshkeycrypt_set'


class SshIdentity(Model):

    fields = {'label', 'username', 'password', 'ssh_key'}
    set_name = 'sshidentity_set'
    mapping = {
        'ssh_key': Mapping(SshKey, many=False),
    }


class SshConfig(Model):

    fields = {'port', 'ssh_identity'}
    set_name = 'sshconfig_set'
    mapping = {
        'ssh_identity': Mapping(SshIdentity, many=False),
    }


class Group(Model):

    fields = {'label', 'parent_group', 'ssh_config'}
    set_name = 'group_set'
    mapping = {
        'ssh_config': Mapping(SshConfig, many=False),
    }


Group.mapping['parent_group'] = Mapping(Group, many=False)


class Host(Model):

    fields = {'label', 'address', 'group', 'tags', 'address', 'ssh_config'}
    set_name = 'host_set'
    mapping = {
        'ssh_config': Mapping(SshConfig, many=False),
        'tags': Mapping(Tag, many=True),
    }


class PFRule(Model):

    fields = {'label', 'host',
              'bound_address', 'local_port', 'hostname', 'remote_port'}
    set_name = 'pfrule_set'
    mapping = {
        'host': Mapping(Host, many=False),
    }
