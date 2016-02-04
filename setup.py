# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from serverauditor_sshconfig import get_version


# pylint: disable=invalid-name
cli_command_name = 'serverauditor'

# pylint: disable=invalid-name
requires = [
    'cliff==1.15',
    'stevedore==1.10.0',
    'requests==2.7.0',
    'cryptography==1.2.2',
    'six==1.10.0',
    'pyopenssl==0.15.1',
    'ndg-httpsclient==0.4.0',
    'cached-property==1.3.0',
]

# pylint: disable=invalid-name
handlers = [
    'sync = serverauditor_sshconfig.sync.commands:SyncCommand',
    'login = serverauditor_sshconfig.account.commands:LoginCommand',
    'logout = serverauditor_sshconfig.account.commands:LogoutCommand',
    'push = serverauditor_sshconfig.cloud.commands:PushCommand',
    'pull = serverauditor_sshconfig.cloud.commands:PullCommand',
    'snippet = serverauditor_sshconfig.handlers:SnippetCommand',
    'snippets = serverauditor_sshconfig.handlers:SnippetsCommand',
    'host = serverauditor_sshconfig.handlers:HostCommand',
    'hosts = serverauditor_sshconfig.handlers:HostsCommand',
    'identity = serverauditor_sshconfig.handlers:SshIdentityCommand',
    'identities = serverauditor_sshconfig.handlers:SshIdentitiesCommand',
    'key = serverauditor_sshconfig.handlers:SshKeyCommand',
    'keys = serverauditor_sshconfig.handlers:SshKeysCommand',
    'group = serverauditor_sshconfig.handlers:GroupCommand',
    'groups = serverauditor_sshconfig.handlers:GroupsCommand',
    'pfrule = serverauditor_sshconfig.handlers:PFRuleCommand',
    'pfrules = serverauditor_sshconfig.handlers:PFRulesCommand',
    'tags = serverauditor_sshconfig.handlers:TagsCommand',
    'info = serverauditor_sshconfig.handlers:InfoCommand',
    'connect = serverauditor_sshconfig.handlers:ConnectCommand',
]


def get_long_description():
    with open('README.rst') as f:
        return f.read()


setup(
    name='serverauditor-sshconfig',
    version=get_version(),
    license='BSD',
    author='Crystalnix',
    author_email='contacts@crystalnix.com',
    url='https://github.com/Crystalnix/serverauditor-sshconfig',
    description='Serverauditor ssh-config utility.',
    long_description=get_long_description(),
    keywords=['serverauditor', 'crystalnix'],
    packages=find_packages(exclude=['tests']),
    install_requires=requires,
    test_suite='nose.collector',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            '{} = serverauditor_sshconfig.main:main'.format(cli_command_name)
        ],
        'serverauditor.handlers': handlers,
        'serverauditor.info.formatters': [
            'ssh = serverauditor_sshconfig.formatters.ssh:SshFormatter',
            'table = cliff.formatters.table:TableFormatter',
            'shell = cliff.formatters.shell:ShellFormatter',
            'value = cliff.formatters.value:ValueFormatter',
            'yaml = cliff.formatters.yaml_format:YAMLFormatter',
            'json = cliff.formatters.json_format:JSONFormatter',
        ],
        'serverauditor.sync.services': [
            # WARNING! It should be removed in production!
            # Other projects should add such endpoint to add services.
            'ssh = serverauditor_sshconfig.sync.services.ssh:SSHService',
        ],
    },
)
