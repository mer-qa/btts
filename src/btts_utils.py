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

from functools import wraps
import dbus.service
import sys
from traceback import print_exception

def dbus_service_method(dbus_interface, **kwargs):
	def ctor(func):
		dbus_wrapped = dbus.service.method(dbus_interface, **kwargs)(func)
		@wraps(func)
		def logger(*args, **kwargs):
			try:
				print("%s.%s(\n\t%s)" % (dbus_interface,
							func.__name__,
							",\n\t".join(map(str, args))))
				return dbus_wrapped(*args, **kwargs)
			except Exception as e:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				print_exception(exc_type, exc_value, exc_traceback)
				print("Exception raised upon D-Bus call", file=sys.stderr)
				raise e
		return logger

	return ctor
