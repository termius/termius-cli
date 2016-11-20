# -*- coding: utf-8 -*-
import subprocess
import unittest
from pathlib2 import Path
from mock import Mock
from termius.core.storage import ApplicationStorage
from termius.core.models.terminal import (
    Host, Group, PFRule, Identity
)


# inspired from
# https://github.com/lacostej/unity3d-bash-completion
class Completion():

    full_cmdline_template = (
        r'source {compfile}; '
        r'COMP_LINE="{COMP_LINE}" COMP_WORDS=({COMP_WORDS}) '
        r'COMP_CWORD={COMP_CWORD} COMP_POINT={COMP_POINT}; '
        r'$(complete -p {program} | '
        r'sed "s/.*-F \\([^ ]*\\) .*/\\1/") && '
        r'echo ${{COMPREPLY[*]}}'
    )

    def prepare(self, program, command):
        self.program = program
        self.COMP_LINE = '%s %s' % (program, command)
        self.COMP_WORDS = self.COMP_LINE.rstrip()

        args = command.split()
        self.COMP_CWORD = len(args)
        self.COMP_POINT = len(self.COMP_LINE)

        if (self.COMP_LINE[-1] == ' '):
            self.COMP_WORDS += ' '
            self.COMP_CWORD += 1

    def run(self, completion_file, program, command):
        self.prepare(program, command)
        full_cmdline = self.full_cmdline_template.format(
            compfile=completion_file, COMP_LINE=self.COMP_LINE,
            COMP_WORDS=self.COMP_WORDS, COMP_POINT=self.COMP_POINT,
            program=self.program, COMP_CWORD=self.COMP_CWORD
        )
        out = subprocess.Popen(
            ['bash', '-i', '-c', full_cmdline],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return out.communicate()


class CompletionTestCase(unittest.TestCase):

    def test_completion_internal(self):
        self.assertEqualCompletion('fake', '',     'fake ',     'fake ',     1, 5)
        self.assertEqualCompletion('fake', ' ',    'fake  ',    'fake ',     1, 6)
        self.assertEqualCompletion('fake', 'a',    'fake a',    'fake a',    1, 6)
        self.assertEqualCompletion('fake', 'aa',   'fake aa',   'fake aa',   1, 7)
        self.assertEqualCompletion('fake', 'a ',   'fake a ',   'fake a ',   2, 7)
        self.assertEqualCompletion('fake', 'a   ', 'fake a   ', 'fake a ',   2, 9)
        self.assertEqualCompletion('fake', 'a a',  'fake a a',  'fake a a',  2, 8)
        self.assertEqualCompletion('fake', 'a a ', 'fake a a ', 'fake a a ', 3, 9)

    def assertEqualCompletion(self, program, cline, line, words, cword, point):
        c = Completion()
        c.prepare(program, cline)
        self.assertEqual(c.program, program)
        self.assertEqual(c.COMP_LINE, line)
        self.assertEqual(c.COMP_WORDS, words)
        self.assertEqual(c.COMP_CWORD, cword)
        self.assertEqual(c.COMP_POINT, point)


class BashCompletionTest(unittest.TestCase):

    def run_complete(self, completion_file, program, command, expected):
        stdout, stderr = Completion().run(completion_file, program, command)
        print(stderr)
        self.assertEqual(stdout.decode('utf-8'), expected + '\n')


class TermiusTestCase(BashCompletionTest):

    program = 'termius'
    completion_file = 'contrib/completion/bash/termius'

    def test_nothing(self):
        self.run_complete(
            '',
            'complete connect fullclean group groups help host hosts '
            'identities identity info key keys login logout pfrule '
            'pfrules pull push snippet snippets sync tags settings'
        )

    def test_subcommand(self):
        self.run_complete('ho', 'host hosts')
        self.run_complete('grou', 'group groups')
        self.run_complete('i', 'identities identity info')

    def test_options_name(self):
        self.run_complete('host --ad', '--address')
        self.run_complete(
            'host -',
            '-h --help --log-file -t --tag -g --group -a --address -p '
            '--port -s --snippet --identity -u --username -P --password '
            '-i --identity-file -d --delete -L --label -S '
            '--strict-host-key-check -T --timeout --use-ssh-key '
            '-k --keep-alive-packages'
        )
        self.run_complete(
            'info -',
            '-h --help --log-file -G --group -H --host -M --no-merge '
            '-f --format -c --column --prefix --noindent '
            '--address --max-width'
        )

    def test_connect_host_label_and_ids(self):
        self.run_complete('connect', '')
        first = self.client.create_host('localhost', 'Asparagales')
        second = self.client.create_host('localhost', 'xanthorrhoeaceae')
        instances = (first, second)
        print((self.client.app_directory / 'storage').read_text())
        self.run_complete('connect ', ids_labels_completion(instances))
        self.run_complete('connect As', 'Asparagales')
        self.run_complete('connect xa', 'xanthorrhoeaceae')

    def test_connect_pfrule_label_and_ids(self):
        self.run_complete('connect', '')
        first_host = self.client.create_host('localhost', 'a')
        first = self.client.create_pfrule(first_host, 2222, 'Asparagales')
        second = self.client.create_pfrule(first_host, 2200, 'xanthorrhoeaceae')
        instances = (first, second)
        print((self.client.app_directory / 'storage').read_text())
        self.run_complete('connect -R ', ids_labels_completion(instances))
        self.run_complete('connect -R As', 'Asparagales')
        self.run_complete('connect -R xa', 'xanthorrhoeaceae')

    def test_info_host_label_and_ids(self):
        self.run_complete('info', '')
        first = self.client.create_host('localhost', 'Asparagales')
        second = self.client.create_host('localhost', 'xanthorrhoeaceae')
        instances = (first, second)
        self.run_complete('info ', ids_labels_completion(instances))
        self.run_complete('info As', 'Asparagales')
        self.run_complete('info xa', 'xanthorrhoeaceae')

    def test_identity_option(self):
        self.client.create_identity('Asparagales1', False)
        first = self.client.create_identity('Asparagales', True)
        second = self.client.create_identity('xanthorrhoeaceae', True)
        instances = (first, second)
        for i in ('host', 'group'):
            self.run_complete('{} --identity '.format(i),
                              ids_labels_completion(instances))
            self.run_complete('{} --identity As'.format(i),
                              'Asparagales')
            self.run_complete('{} --identity xa'.format(i),
                              'xanthorrhoeaceae')

    def test_info_group_label_and_ids(self):
        self.run_complete('info', '')
        first = self.client.create_group('Asparagales')
        second = self.client.create_group('xanthorrhoeaceae')
        instances = (first, second)
        for option in ('-g', '--group'):
            subcommand = 'info {} '.format(option)
            self.run_complete(subcommand, ids_labels_completion(instances))
            self.run_complete(subcommand + ' As'.format(option), 'Asparagales')
            self.run_complete(subcommand + ' xa', 'xanthorrhoeaceae')

    def test_update_entity(self):
        entity = 'host'
        self.run_complete(entity, '')
        first = self.client.create_host('localhost', 'Asparagales')
        second = self.client.create_host('localhost', 'xanthorrhoeaceae')
        instances = (first, second)
        self.run_complete(entity + ' ', ids_labels_completion(instances))
        self.run_complete(entity + ' As', 'Asparagales')
        self.run_complete(entity + ' xa', 'xanthorrhoeaceae')

    def test_list_format_types(self):
        for subcommand  in ('hosts', 'groups', 'tags', 'identities', 'snippets', 'pfrules', 'keys'):
            self.run_complete(subcommand + ' -f ', 'csv json table value yaml')
            self.run_complete(subcommand + ' --format ', 'csv json table value yaml')

    def run_complete(self, command, expected):
        super(TermiusTestCase, self).run_complete(
            self.completion_file, self.program, command, expected
        )

    def setUp(self):
        self.client = TermiusClient()

    def tearDown(self):
        self.client.clean()


class TermiusClient(object):

    def __init__(self):
        self.app_directory = Path('~/.termius/').expanduser()
        self.command_mock = Mock(**{'app.directory_path': self.app_directory})
        self.prepare()

    def create_identity(self, label, is_visible):
        return self._create_instance(
            Identity, label=label, is_visible=is_visible
        )

    def create_host(self, address, label):
        return self._create_instance(Host, label=label, address=address)

    def create_pfrule(self, host_id, local_port, label):
        return self._create_instance(
            PFRule, label=label,
            pftype='L', local_port=local_port,
            remote_port=22, hostname='localhost'
        )

    def create_group(self, label):
        return self._create_instance(Group, label=label)

    def _create_instance(self, model, **kwargs):
        instance = model(**kwargs)
        with self.storage:
            return self.storage.save(instance)

    def prepare(self):
        self.clean()
        if not self.app_directory.is_dir():
            self.app_directory.mkdir()
        self.storage = ApplicationStorage(self.command_mock)

    def clean(self):
        if self.app_directory.is_dir():
            self._clean_dir(self.app_directory)

    def _clean_dir(self, dir_path):
        [self._clean_dir(i) for i in dir_path.iterdir() if i.is_dir()]
        [i.unlink() for i in dir_path.iterdir() if i.is_file()]
        dir_path.rmdir()


def ids_labels_completion(instances):
    return ' '.join(['{0.label}'.format(i) for i in instances])
