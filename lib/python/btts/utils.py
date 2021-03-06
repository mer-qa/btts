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
import io
import logging
import sys

log = logging.getLogger(__name__)

def dbus_service_method(dbus_interface, **kwargs):
	def ctor(func):
		dbus_wrapped = dbus.service.method(dbus_interface, **kwargs)(func)
		@wraps(func)
		def logger(*args, **kwargs):
			try:
				log.debug("CALL %s.%s(\n\t%s)" % (dbus_interface,
							func.__name__,
							",\n\t".join(map(str, args))))
				return dbus_wrapped(*args, **kwargs)
			except Exception as e:
				log.exception("Exception raised upon D-Bus call")
				raise e
		return logger

	return ctor

def dbus_service_signal(dbus_interface, **kwargs):
	def ctor(func):
		dbus_wrapped = dbus.service.signal(dbus_interface, **kwargs)(func)
		@wraps(func)
		def logger(*args, **kwargs):
			try:
				log.debug("EMIT %s.%s(\n\t%s)" % (dbus_interface,
							func.__name__,
							",\n\t".join(map(str, args))))
				return dbus_wrapped(*args, **kwargs)
			except Exception as e:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				log.exception("Exception raised upon D-Bus signal emission")
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

def sendfile(ofile, ifile, max_size):
    to_write = max_size
    while True:
        to_read = min(io.DEFAULT_BUFFER_SIZE, to_write)
        if to_read == 0:
            break

        b = ifile.read(to_read)
        if not b:
            break

        ofile.write(b)
        to_write -= len(b)

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
