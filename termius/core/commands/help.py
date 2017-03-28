import sys
import traceback

from cliff.help import (
    HelpAction as BaseHelpAction,
    HelpCommand as BaseHelpCommand
)


class HelpAction(BaseHelpAction):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands:\n')
        command_manager = app.command_manager
        for name, ep in sorted(command_manager):
            try:
                factory = ep.load()
            except Exception:
                app.stdout.write('Could not load %r\n' % ep)
                if namespace.debug:
                    traceback.print_exc(file=app.stdout)
                continue
            try:
                cmd = factory(app, None)
                if cmd.deprecated:
                    continue
            except Exception as err:
                app.stdout.write('Could not instantiate %r: %s\n' % (ep, err))
                if namespace.debug:
                    traceback.print_exc(file=app.stdout)
                continue
            one_liner = cmd.get_description().split('\n')[0]
            app.stdout.write('  %-20s  %s\n' % (name, one_liner))
        sys.exit(0)


class HelpCommand(BaseHelpCommand):
    """display the command specific help message"""

    def take_action(self, parsed_args):
        if parsed_args.cmd:
            try:
                the_cmd = self.app.command_manager.find_command(
                    parsed_args.cmd,
                )
                cmd_factory, cmd_name, search_args = the_cmd
            except ValueError:
                # Did not find an exact match
                cmd = parsed_args.cmd[0]
                fuzzy_matches = [
                    k[0] for k in self.app.command_manager
                    if k[0].startswith(cmd)
                ]
                if not fuzzy_matches:
                    raise
                self.app.stdout.write('Command "%s" matches:\n' % cmd)
                for fm in sorted(fuzzy_matches):
                    self.app.stdout.write('  %s\n' % fm)
                return
            self.app_args.cmd = search_args
            cmd = cmd_factory(self.app, self.app_args)
            full_name = (cmd_name
                         if self.app.interactive_mode
                         else ' '.join([self.app.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
            cmd_parser.print_help(self.app.stdout)
        else:
            action = HelpAction(None, None, default=self.app)
            action(self.app.parser, self.app.options, None, None)
        return 0
