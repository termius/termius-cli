from __future__ import print_function

import abc
import pprint
import time


class Logger(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def log(self, message, *args, **kwargs):
        pass


class PrettyLogger(Logger):

    COLOR_END = '\033[0m'
    COLOR_BOLD = '\033[1m'
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'end': COLOR_END
    }

    def log(self, message, sleep=0.5, color='end', color_bold=False, is_pprint=False, *args, **kwargs):
        print(self.COLORS.get(color, self.COLOR_END), end='')
        if color_bold:
            print(self.COLOR_BOLD, end='')
        if is_pprint:
            pprint.pprint(message, *args, **kwargs)
        else:
            print(message, end='', *args, **kwargs)
        print(self.COLOR_END)
        if sleep:
            time.sleep(sleep)
        return
