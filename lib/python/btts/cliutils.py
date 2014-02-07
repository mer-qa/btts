from __future__ import absolute_import, print_function, unicode_literals

from   contextlib import ContextDecorator
import sys

class Failure(Exception):
    pass

class BadUsage(Exception):
    pass

class failure_on(ContextDecorator):
    def __init__(self, exc_types):
        ContextDecorator.__init__(self)
        self.exc_types = exc_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and any(map(lambda t: issubclass(exc_type, t), self.exc_types)):
            raise Failure(str(exc_value)).with_traceback(traceback)
        return False

class bad_usage_on(ContextDecorator):
    def __init__(self, exc_types):
        ContextDecorator.__init__(self)
        self.exc_types = exc_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and any(map(lambda t: issubclass(exc_type, t), self.exc_types)):
            raise BadUsage(str(exc_value)).with_traceback(traceback)
        return False

class error_handler:
    def __init__(self, argparser):
        self._argparser = argparser

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is BadUsage:
            print(exc_value, file=sys.stderr)
            self._argparser.print_usage()
            sys.exit(1)
        if exc_type is Failure:
            print("Failed: %s" % (exc_value), file=sys.stderr)
            sys.exit(1)
        return False

# For argument parsing
def boolean(string):
    if string in ['true', 'yes', '1', 'on']:
        return True
    elif string in ['false', 'no', '0', 'off']:
        return False
    else:
        raise TypeError
