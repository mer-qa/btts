#
# BTTS - BlueTooth Test Suite
#
# Copyright (C) 2014 Jolla Ltd.
# Contact: Martin Kampas <martin.kampas@jollamobile.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals

import dbus
import sys

class Failure(Exception):
    pass

class BadUsage(Exception):
    pass

def _match_exc(matched_exc, wanted_exc_type):
    if isinstance(matched_exc, wanted_exc_type):
        return True
    if isinstance(matched_exc, dbus.DBusException):
        wanted_dbus_error_name = getattr(wanted_exc_type, '_dbus_error_name', None)
        if wanted_dbus_error_name is not None:
            if matched_exc.get_dbus_name() == wanted_dbus_error_name:
                return True
    return False

if sys.version_info.major > 2:
    from contextlib import ContextDecorator

    class failure_on(ContextDecorator):
        def __init__(self, exc_types):
            ContextDecorator.__init__(self)
            self.exc_types = exc_types

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            if exc_type and any(map(lambda t: _match_exc(exc_value, t),
                                    self.exc_types)):
                raise Failure(str(exc_value)).with_traceback(traceback)
            return False

    class bad_usage_on(ContextDecorator):
        def __init__(self, exc_types):
            ContextDecorator.__init__(self)
            self.exc_types = exc_types

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            if exc_type and any(map(lambda t: _match_exc(exc_value, t),
                                    self.exc_types)):
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
