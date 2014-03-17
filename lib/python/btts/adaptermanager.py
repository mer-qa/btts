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

from gi.repository import Gio
import copy
import dbus
import glob
import logging
import os
import re
import warnings

from btts.adapter import Adapter

log = logging.getLogger(__name__)

_ADAPTERS_FILE = "/etc/btts/adapters"
_GSETTINGS_SCHEMA = "org.merproject.btts"

class AdapterManager:
    class Error(Exception):
        pass

    class AdapterNotSetError(Error):
        def __init__(self):
            AdapterManager.Error.__init__(self, "Adapter not set")

    class NoSuchAdapterError(Error):
        def __init__(self, adapter):
            AdapterManager.Error.__init__(self, "%s: No such adapter" % (adapter))
            self.adapter = adapter

    def __init__(self):
        self.settings = Gio.Settings.new(_GSETTINGS_SCHEMA)

        self._name_by_address = self._read_names()
        self._address_by_name = dict(zip(self._name_by_address.values(),
                                         self._name_by_address.keys()))

        self._alias_by_address = self._read_aliases()
        self._address_by_alias = dict(zip(self._alias_by_address.values(),
                                          self._alias_by_address.keys()))

        for alias, address in copy.deepcopy(self._address_by_alias).items():
            if address not in self._address_by_name.values():
                log.warning("Invalid record in %s: %s: No such adapter" %
                            (_ADAPTERS_FILE, address))
                del self._address_by_alias[alias]

    def get_adapter_no_alias(self):
        name = self.settings.get_string("adapter")
        if not name:
            raise self.AdapterNotSetError()
        if not name in self._address_by_name:
            log.warning("%s: Stale setting. No such adapter." % (name))
            raise self.AdapterNotSetError()
        return name

    def get_adapter(self):
        name = self.get_adapter_no_alias()
        address = self._address_by_name[name]
        return self._alias_by_address.get(address, name)

    def set_adapter(self, name_or_alias):
        if name_or_alias in self._address_by_alias:
            address = self._address_by_alias[name_or_alias]
            name = self._name_by_address[address]
        elif name_or_alias in self._address_by_name:
            name = name_or_alias
        else:
            raise self.NoSuchAdapterError(adapter=name_or_alias)

        try:
            adapter = Adapter()
            adapter.properties_iface.Set('org.bluez.Adapter1', 'Alias', '')
            # Even if DOWN, it can still be discovered until explicitly disabled
            adapter.discoverable = False
            adapter.powered = False
        except self.AdapterNotSetError:
            pass

        self.settings.set_string("adapter", name)

        try:
            adapter = Adapter()
            adapter.properties_iface.Set('org.bluez.Adapter1', 'Alias',
                                         self.get_host_alias())
        except self.AdapterNotSetError:
            pass

    def get_host_alias(self):
        host_alias = self.settings.get_string("host-alias")
        return host_alias

    def set_host_alias(self, host_alias):
        self.settings.set_string("host-alias", host_alias)
        try:
            adapter = Adapter()
            adapter.properties_iface.Set('org.bluez.Adapter1', 'Alias', host_alias)
        except self.AdapterNotSetError:
            pass

    @staticmethod
    def _read_aliases():
        aliases = {}
        try:
            with open(_ADAPTERS_FILE, "r") as adapters_file:
                aliases = dict(re.findall(r'^\s*([^#]\S+)\s+(.*)\s*$',
                                          adapters_file.read(),
                                          re.MULTILINE))
                aliases = dict(zip(map(lambda s: s.lower(), aliases.keys()),
                                   aliases.values()))
        except FileNotFoundError:
            pass
        return aliases

    @staticmethod
    def _read_names():
        names = {}
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                 "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        for path, properties in objects.items():
            adapter_properties = properties.get('org.bluez.Adapter1')
            if adapter_properties is not None:
                name = os.path.basename(path)
                address = adapter_properties['Address'].lower()
                names[address] = name
        return names

