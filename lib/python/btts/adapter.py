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
import subprocess
import sys

import btts

class Adapter:
    FEATURES = [
            'simple pairing',
            ]

    def __init__(self):
        self._config = btts.Config()
        name = self._config.get_adapter_no_alias()

        self._adapter_object = None
        self._properties_iface = None

        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                 "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        for path, properties in objects.items():
            adapter_properties = properties.get('org.bluez.Adapter1')
            if adapter_properties is not None and path.endswith(name):
                self._adapter_object = bus.get_object('org.bluez', path)
                self._adapter_iface = dbus.Interface(self._adapter_object,
                                                     'org.bluez.Adapter1')
                self._properties_iface = dbus.Interface(self._adapter_object,
                                                        dbus.PROPERTIES_IFACE)
                break

    def _ensure_ready(self):
        if not self._adapter_object:
            raise btts.Config.AdapterNotSetError()

    @property
    def path(self):
        self._ensure_ready()
        return self._adapter_object.object_path

    @property
    def address(self):
        self._ensure_ready()
        return self._properties_iface.Get('org.bluez.Adapter1', 'Address')

    def has_feature(self, feature):
        name = self._config.get_adapter_no_alias()
        hciconfig = ['hciconfig', name, 'features']
        features = subprocess.check_output(hciconfig, universal_newlines = True)
        return ''.join(['<', feature, '>']) in features

    @property
    def powered(self):
        self._ensure_ready()
        return self._properties_iface.Get('org.bluez.Adapter1', 'Powered')

    @powered.setter
    def powered(self, powered):
        self._ensure_ready()
        return self._properties_iface.Set('org.bluez.Adapter1', 'Powered', powered)

    @property
    def discoverable(self):
        self._ensure_ready()
        return self._properties_iface.Get('org.bluez.Adapter1', 'Discoverable')

    @discoverable.setter
    def discoverable(self, discoverable):
        self._ensure_ready()
        self._properties_iface.Set('org.bluez.Adapter1', 'Discoverable',
                                   discoverable)
        if discoverable:
            self._properties_iface.Set('org.bluez.Adapter1',
                                       'DiscoverableTimeout', dbus.UInt32(0))

    def scan(self, refresh=False):
        self._ensure_ready()

        try:
            self._adapter_iface.StopDiscovery()
        except dbus.DBusException as e:
            if e.get_dbus_name() != 'org.bluez.Error.Failed':
                raise e

        name = self._config.get_adapter_no_alias()
        args = ['hcitool', '-i', name, 'scan', '--flush']
        if refresh:
            args.append('--refresh')
        subprocess.call(args, stdout=sys.stderr)

        try:
            self._adapter_iface.StartDiscovery()
        except dbus.DBusException as e:
            if e.get_dbus_name() != 'org.bluez.Error.InProgress':
                raise e

    @property
    def adapter_iface(self):
        self._ensure_ready()
        return self._adapter_iface

    @property
    def properties_iface(self):
        self._ensure_ready()
        return self._properties_iface
