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

from btts.adapter import Adapter
from btts.device import Device

log = logging.getLogger(__name__)

_ADAPTERS_FILE = "/etc/btts/adapters"
_GSETTINGS_SCHEMA = "org.merproject.btts"

class Config:
    class Error(Exception):
        pass

    class NoSuchAdapterError(Error):
        def __init__(self, adapter):
            Config.Error.__init__(self, "%s: No such adapter" % (adapter))
            self.adapter = adapter

    class AdapterNotSetError(Error):
        def __init__(self):
            Config.Error.__init__(self, "Adapter not set")

    class InvalidAddressError(Error):
        def __init__(self, address):
            Config.Error.__init__(self, "%s: Not a valid address" % (address))
            self.address = address

    class DeviceNotSetError(Error):
        def __init__(self):
            Config.Error.__init__(self, "Device not set")

    class NoSuchProfileError(Error):
        def __init__(self, profile):
            Config.Error.__init__(self, "%s: No such profile" % (profile))
            self.profile = profile

    class TimeoutError(Error):
        def __init__(self):
            Config.Error.__init__(self, "Timeout")

    def __init__(self):
        self._adapter_manager = Config._AdapterManager()
        self._device_manager = Config._DeviceManager()
        self._profile_manager = Config._ProfileManager()

    def get_adapter_no_alias(self):
        return self._adapter_manager.get_adapter_no_alias()

    def get_adapter(self):
        return self._adapter_manager.get_adapter()

    def set_adapter(self, name_or_alias):
        self._adapter_manager.set_adapter(name_or_alias)

    def get_host_alias(self):
        return self._adapter_manager.get_host_alias()

    def set_host_alias(self, host_alias):
        self._adapter_manager.set_host_alias(host_alias)

    @property
    def device_address(self):
        return self._device_manager.device_address()

    @device_address.setter
    def set_device_address(self, address):
        self._device_manager.set_device_address(address)

    def get_profiles_state(self, profiles=[]):
        return self._profile_manager.get_profiles_state(profiles)

    def enable_profile(self, profile, enable=True):
        self._profile_manager.enable_profile(profile, enable)

    class _AdapterManager:
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
                raise Config.AdapterNotSetError()
            if not name in self._address_by_name:
                log.warning("%s: Stale setting. No such adapter." % (name))
                raise Config.AdapterNotSetError()
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
                raise Config.NoSuchAdapterError(adapter=name_or_alias)

            try:
                adapter = Adapter()
                adapter.properties_iface.Set('org.bluez.Adapter1', 'Alias', '')
                # Even if DOWN, it can still be discovered until explicitly disabled
                adapter.discoverable = False
                adapter.powered = False
            except Config.AdapterNotSetError:
                pass

            self.settings.set_string("adapter", name)

            try:
                adapter = Adapter()
                adapter.properties_iface.Set('org.bluez.Adapter1', 'Alias',
                                             self.get_host_alias())
            except Config.AdapterNotSetError:
                pass

        def get_host_alias(self):
            host_alias = self.settings.get_string("host-alias")
            return host_alias

        def set_host_alias(self, host_alias):
            self.settings.set_string("host-alias", host_alias)
            try:
                adapter = Adapter()
                adapter.properties_iface.Set('org.bluez.Adapter1', 'Alias', host_alias)
            except Config.AdapterNotSetError:
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

    class _DeviceManager:
        def __init__(self):
            self.settings = Gio.Settings.new(_GSETTINGS_SCHEMA)

        def device_address(self):
            address = self.settings.get_string("device").lower()
            if not address:
                raise Config.DeviceNotSetError()
            return address

        def set_device_address(self, address):
            if not Device.is_valid_address(address):
                raise Config.InvalidAddressError(address)

            self.settings.set_string("device", address.lower())

    class _ProfileManager:
        _REASONABLE_TIMEOUT = 5000

        # keep in sync with conf/dbus/btts.conf
        _unit_by_bt_profile = {
                'hfp': 'ofono.service',
                'a2dp': 'btts-pulseaudio.service'
                }
        valid_profile_names = _unit_by_bt_profile.keys()

        def __init__(self):
            self._bus = dbus.SystemBus()
            manager_object = self._bus.get_object('org.freedesktop.systemd1',
                                                  '/org/freedesktop/systemd1')
            self._systemd_manager = dbus.Interface(
                    manager_object, "org.freedesktop.systemd1.Manager")
            self._job = None

        def get_profiles_state(self, profiles=[]):
            states = {}
            for profile, unit_name in self._unit_by_bt_profile.items():
                if profiles and profile not in profiles:
                    continue
                unit_properties = self._get_unit_properties(unit_name)
                active_state = unit_properties.Get('org.freedesktop.systemd1.Unit',
                                                   'ActiveState')
                states[profile] = active_state == 'active'
            return states

        def enable_profile(self, profile, enable=True):
            assert not self._job
            if not profile in self.valid_profile_names:
                raise Config.NoSuchProfileError(profile)

            unit_name = self._unit_by_bt_profile[profile]
            unit = self._get_unit(unit_name)

            self._job_result = None

            self._systemd_manager.connect_to_signal("JobRemoved",
                                                    self._on_job_removed)

            if enable:
                self._job = unit.Start("replace")
            else:
                self._job = unit.Stop("replace")

            self._loop = GObject.MainLoop()
            GObject.timeout_add(_REASONABLE_TIMEOUT, self._loop.quit)
            self._loop.run()

            if self._job_result == None:
                raise Config.TimeoutError()
            if self._job_result != "done":
                raise Config.Error("Failed to start/stop system service %s: %s" %
                                   (unit_name, self._job_result))

        def _get_unit(self, unit_name):
            unit_path = self._systemd_manager.GetUnit(unit_name)
            unit_object = self._bus.get_object('org.freedesktop.systemd1',
                                               unit_path)
            unit = dbus.Interface(unit_object,
                                  dbus_interface='org.freedesktop.systemd1.Unit')
            return unit

        def _get_unit_properties(self, unit_name):
            unit_path = self._systemd_manager.GetUnit(unit_name)
            unit_object = self._bus.get_object('org.freedesktop.systemd1',
                                               unit_path)
            properties = dbus.Interface(unit_object,
                                        dbus_interface=dbus.PROPERTIES_IFACE)
            return properties

        def _on_job_removed(self, id, job, unit, result):
            if job == self._job:
                self._job_result = result
                self._loop.quit()
                self._job = None
