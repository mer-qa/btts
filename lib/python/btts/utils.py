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
				print("CALL %s.%s(\n\t%s)" % (dbus_interface,
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

def dbus_service_signal(dbus_interface, **kwargs):
	def ctor(func):
		dbus_wrapped = dbus.service.signal(dbus_interface, **kwargs)(func)
		@wraps(func)
		def logger(*args, **kwargs):
			try:
				print("EMIT %s.%s(\n\t%s)" % (dbus_interface,
							func.__name__,
							",\n\t".join(map(str, args))))
				return dbus_wrapped(*args, **kwargs)
			except Exception as e:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				print_exception(exc_type, exc_value, exc_traceback)
				print("Exception raised upon D-Bus signal emission",
						file=sys.stderr)
				raise e
		return logger

	return ctor

def signal(func):
    class Signal:
        def __init__(self):
            self.slots = set()

        def __call__(self, *args):
            for slot in self.slots:
                slot(*args)

        def connect(self, slot):
            self.slots.add(slot)

        def disconnect(self, slot):
            self.slots.remove(slot)
    return Signal()

if __name__ == '__main__':
    def test_signal():
        class Sender:
            def foo(self, num):
                self.foo_called(num)

            @signal
            def foo_called(self, num):
                pass

        class Receiver:
            def on_foo_called(self, num):
                print('foo called with %d' % (num))

        sender = Sender()
        receiver = Receiver()

        sender.foo_called.connect(receiver.on_foo_called)

        sender.foo(3)

    test_signal()
