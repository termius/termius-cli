from distutils.core import setup


name = 'serverauditor_sshconfig'


def get_version():
    from serverauditor_sshconfig import __version__
    return '.'.join(map(str, __version__))


setup(
    name=name,
    version=get_version(),
    packages=['serverauditor_sshconfig', 'serverauditor_sshconfig.core'],
    url='https://github.com/Crystalnix/serverauditor-sshconfig',
    license='MIT',
    author='Yan Kalchevskiy',
    author_email='yan.kalchevskiy@crystalnix.com',
    description='Serverauditor ssh-config utility.',
    scripts=['serverauditor_sshconfig/sa_export.py', 'serverauditor_sshconfig/sa_import.py'],
    requires=[
        'pycrypto',
    ]
)
