# -*- coding: utf-8 -*-
"""Config-like for paver tool."""
from paver.easy import task, sh, path  # noqa

# pylint: disable=invalid-name
cli_command_name = 'serverauditor'


@task
def lint():
    """Check code style and conventions."""
    sh('prospector')


@task
def bats():
    """Run tests on CLI usage."""
    sh('bats --tap tests/integration')


@task
def nosetests():
    """Run unit tests."""
    sh('nosetests')


@task
def coverage():
    """Run test and collect coverage."""
    sh('nosetests --with-coverage')
    sh('coverage xml')


@task
def create_compeletion(info):
    """Generate bash completion."""
    completion_dir = path('contrib/completion/bash')
    if not completion_dir.exists():
        completion_dir.makedirs_p()
    completion_path = completion_dir / cli_command_name
    if completion_path.exists():
        info('Completion exists')
    else:
        sh('{} complete > {}'.format(cli_command_name, completion_path))


@task
def clean_compeletion(info):
    """Generate bash completion."""
    completion_path = path('contrib/bash/complete') / cli_command_name
    completion_path.remove()
    info('Completion exists')
