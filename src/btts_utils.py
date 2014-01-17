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

from contextlib import ContextDecorator
import dbus.service
import sys
from traceback import print_exception

class exceptionslogged(ContextDecorator):
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if exc_type:
			print_exception(exc_type, exc_value, traceback)
			print("Exception raised upon D-Bus call", file=sys.stderr)
		return False

def dbus_service_method(dbus_interface, **kwargs):
	return lambda func: exceptionslogged()(
			dbus.service.method(dbus_interface, **kwargs)(func))
