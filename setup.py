# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from termius import __version__


# pylint: disable=invalid-name
cli_command_name = 'termius'

# pylint: disable=invalid-name
requires = [
    'cliff>=1.15',
    'stevedore>=1.10.0',
    'requests>=2.7.0',
    'cryptography>=1.3.1',
    'six>=1.10.0',
    'ndg-httpsclient>=0.4.0',
    'pyopenssl>=0.15.1',
    'cached-property>=1.3.0',
    'paramiko>=1.16.0',
    'pathlib2>=2.1.0',
    'blinker>=1.4',
    'google-measurement-protocol>=0.1.6',
]

# pylint: disable=invalid-name
handlers = [
    'import-ssh-config = termius.porting.commands:SSHImportCommand',
    'export-ssh-config = termius.porting.commands:SSHExportCommand',
    'login = termius.account.commands:LoginCommand',
    'logout = termius.account.commands:LogoutCommand',
    'settings = termius.account.commands:SettingsCommand',
    'push = termius.cloud.commands:PushCommand',
    'pull = termius.cloud.commands:PullCommand',
    'fullclean = termius.cloud.commands:FullCleanCommand',
    'snippet = termius.handlers:SnippetCommand',
    'snippets = termius.handlers:SnippetsCommand',
    'host = termius.handlers:HostCommand',
    'hosts = termius.handlers:HostsCommand',
    'identity = termius.handlers:IdentityCommand',
    'identities = termius.handlers:IdentitiesCommand',
    'key = termius.handlers:SshKeyCommand',
    'keys = termius.handlers:SshKeysCommand',
    'group = termius.handlers:GroupCommand',
    'groups = termius.handlers:GroupsCommand',
    'pfrule = termius.handlers:PFRuleCommand',
    'pfrules = termius.handlers:PFRulesCommand',
    'tags = termius.handlers:TagsCommand',
    'info = termius.handlers:InfoCommand',
    'connect = termius.handlers:ConnectCommand',
    'crypto = termius.cloud.commands:CryptoCommand',
    'init = termius.handlers:InitCommand'
]


def get_long_description():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError):
        with open('README.md') as f:
            return f.read()


setup(
    name='termius',
    version=__version__,
    license='BSD',
    author='Crystalnix',
    author_email='contacts@crystalnix.com',
    url='https://github.com/Crystalnix/termius-cli',
    description='Termius ssh-config utility.',
    long_description=get_long_description(),
    keywords=['termius', 'crystalnix'],
    packages=find_packages(exclude=['tests']),
    install_requires=requires,
    test_suite='nose.collector',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            '{} = termius.main:main'.format(cli_command_name)
        ],
        'termius.handlers': handlers,
        'termius.info.formatters': [
            'ssh = termius.formatters.ssh:SshFormatter',
            'table = cliff.formatters.table:TableFormatter',
            'shell = cliff.formatters.shell:ShellFormatter',
            'value = cliff.formatters.value:ValueFormatter',
            'yaml = cliff.formatters.yaml_format:YAMLFormatter',
            'json = cliff.formatters.json_format:JSONFormatter',
        ],
        'termius.sync.providers': [
            'ssh = termius.sync.providers.ssh:SSHService',
        ],
    },
)
