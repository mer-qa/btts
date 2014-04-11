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

import dbus

import btts

class VoiceCall:
    class Error(Exception):
        pass

    class NotReadyError(Error):
        def __init__(self):
            VoiceCall.Error.__init__(self, 'Not ready')

    def __init__(self):
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.ofono', '/'),
                                 'org.ofono.Manager')

        self._modem_object = None

        device_address = btts.Config().device.upper()
        modems = manager.GetModems()
        for path, properties in modems:
            try:
                if (properties['Type'] == 'hfp' and
                        properties['Serial'] == device_address):
                    self._modem_object = bus.get_object('org.ofono', path)
                    break
            except KeyError:
                pass

    def __getattr__(self, member):
        self._ensure_ready()

        if member.startswith('__') and member.endswith('__'):
            raise AttributeError(member)
        else:
            return self._modem_object.get_dbus_method(
                    member, 'org.ofono.VoiceCallManager')

    def _ensure_ready(self):
        if not self._modem_object:
            raise self.NotReadyError()
