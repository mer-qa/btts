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
