from setuptools import setup, find_packages

from serverauditor_sshconfig import __version__


def get_version():
    return '.'.join(map(str, __version__))


def get_long_description():
    with open('README.rst') as f:
        return f.read()


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
    scripts=['serverauditor_sshconfig/serverauditor'],
    install_requires=['pycrypto==2.6'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ]
)
