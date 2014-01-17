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
