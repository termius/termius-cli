# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from serverauditor_sshconfig import get_version


# pylint: disable=invalid-name
cli_command_name = 'serverauditor'

# pylint: disable=invalid-name
requires = [
    'cliff>=1.15',
    'stevedore>=1.10.0',
    'requests>=2.7.0',
    'cryptography>=1.3.1',
    'six>=1.10.0',
    'pyopenssl>=0.15.1',
    'ndg-httpsclient>=0.4.0',
    'cached-property>=1.3.0',
    'paramiko>=1.16.0',
    'pathlib2>=2.1.0',
    'blinker>=1.4',
]

# pylint: disable=invalid-name
handlers = [
    'sync = serverauditor_sshconfig.sync.commands:SyncCommand',
    'login = serverauditor_sshconfig.account.commands:LoginCommand',
    'logout = serverauditor_sshconfig.account.commands:LogoutCommand',
    'settings = serverauditor_sshconfig.account.commands:SettingsCommand',
    'push = serverauditor_sshconfig.cloud.commands:PushCommand',
    'pull = serverauditor_sshconfig.cloud.commands:PullCommand',
    'fullclean = serverauditor_sshconfig.cloud.commands:FullCleanCommand',
    'snippet = serverauditor_sshconfig.handlers:SnippetCommand',
    'snippets = serverauditor_sshconfig.handlers:SnippetsCommand',
    'host = serverauditor_sshconfig.handlers:HostCommand',
    'hosts = serverauditor_sshconfig.handlers:HostsCommand',
    'identity = serverauditor_sshconfig.handlers:IdentityCommand',
    'identities = serverauditor_sshconfig.handlers:IdentitiesCommand',
    'key = serverauditor_sshconfig.handlers:SshKeyCommand',
    'keys = serverauditor_sshconfig.handlers:SshKeysCommand',
    'group = serverauditor_sshconfig.handlers:GroupCommand',
    'groups = serverauditor_sshconfig.handlers:GroupsCommand',
    'pfrule = serverauditor_sshconfig.handlers:PFRuleCommand',
    'pfrules = serverauditor_sshconfig.handlers:PFRulesCommand',
    'tags = serverauditor_sshconfig.handlers:TagsCommand',
    'info = serverauditor_sshconfig.handlers:InfoCommand',
    'connect = serverauditor_sshconfig.handlers:ConnectCommand',
    'crypto = serverauditor_sshconfig.cloud.commands:CryptoCommand',
]


def get_long_description():
    with open('README.md') as f:
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
        'serverauditor.sync.providers': [
            'ssh = serverauditor_sshconfig.sync.providers.ssh:SSHService',
        ],
    },
)
