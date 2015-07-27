from setuptools import setup, find_packages

from serverauditor_sshconfig import __version__


def get_version():
    return '.'.join(map(str, __version__))


def get_long_description():
    with open('README.rst') as f:
        return f.read()

requires = [
    'cliff==1.13',
    'stevedore==1.6.0',
    'requests==2.7.0',
    'pycrypto==2.6',
    'six==1.9.0',
    'pyopenssl',
    'ndg-httpsclient',
    'pyasn1',
]


setup(
    name='serverauditor-sshconfig',
    version=get_version(),
    license='BSD',
    author='Yan Kalchevskiy',
    author_email='yan.kalchevskiy@crystalnix.com',
    url='https://github.com/Crystalnix/serverauditor-sshconfig',
    description='Serverauditor ssh-config utility.',
    long_description=get_long_description(),
    keywords=['serverauditor', 'crystalnix'],
    packages=find_packages(),
    install_requires=requires,
    zip_safe=False,
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
            'serverauditor = serverauditor_sshconfig.main:main'
        ],
        'serverauditor.handlers': [
            'sync = serverauditor_sshconfig.sync.commands:SyncCommand',
            'use = serverauditor_sshconfig.cloud.commands:UseGroupCommand',
            'snippet = serverauditor_sshconfig.cloud.commands:SnippetCommand',
            'snippets = serverauditor_sshconfig.cloud.commands:SnippetsCommand',
            'host = serverauditor_sshconfig.cloud.commands:HostCommand',
            'hosts = serverauditor_sshconfig.cloud.commands:HostsCommand',
            'identity = serverauditor_sshconfig.cloud.commands:SshIdentityCommand',
            'identities = serverauditor_sshconfig.cloud.commands:SshIdentitiesCommand',
            'group = serverauditor_sshconfig.cloud.commands:GroupCommand',
            'groups = serverauditor_sshconfig.cloud.commands:GroupsCommand',
            'pfrule = serverauditor_sshconfig.cloud.commands:PFRuleCommand',
            'pfrules = serverauditor_sshconfig.cloud.commands:PFRulesCommand',
            'tags = serverauditor_sshconfig.cloud.commands:TagsCommand',
            'login = serverauditor_sshconfig.account.commands:LoginCommand',
            'logout = serverauditor_sshconfig.account.commands:LogoutCommand',
            'push = serverauditor_sshconfig.cloud.commands:PushCommand',
            'pull = serverauditor_sshconfig.cloud.commands:PullCommand',
            'info = serverauditor_sshconfig.cloud.commands:InfoCommand',
            'connect = serverauditor_sshconfig.handlers:ConnectCommand',
        ],
        'serverauditor.sync.services': [
            # WARNING! It should be removed in production!
            # Other projects should add such endpoint to add services.
            'aws = serverauditor_sshconfig.sync.services.aws:AWSService',
        ],
    },
)
