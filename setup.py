from setuptools import setup, find_packages

from serverauditor_sshconfig import __version__


def get_version():
    return '.'.join(map(str, __version__))


def get_long_description():
    with open('README.rst') as f:
        return f.read()

requires = [
    'cliff==1.13'
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
            'sync = serverauditor_sshconfig.handlers:SyncCommand',
            'use = serverauditor_sshconfig.handlers:UseGroupCommand',
            'host = serverauditor_sshconfig.handlers:HostCommand',
            'group = serverauditor_sshconfig.handlers:GroupCommand',
            'hosts = serverauditor_sshconfig.handlers:HostsCommand',
            'groups = serverauditor_sshconfig.handlers:GroupsCommand',
            'pfrule = serverauditor_sshconfig.handlers:PFRuleCommand',
            'pfrules = serverauditor_sshconfig.handlers:PFRulesCommand',
            'tags = serverauditor_sshconfig.handlers:TagsCommand',
            'login = serverauditor_sshconfig.handlers:LoginCommand',
            'logout = serverauditor_sshconfig.handlers:LogoutCommand',
            'push = serverauditor_sshconfig.handlers:PushCommand',
            'pull = serverauditor_sshconfig.handlers:PullCommand',
            'info = serverauditor_sshconfig.handlers:InfoCommand',
            'connect = serverauditor_sshconfig.handlers:ConnectCommand',
        ],
    },
)
