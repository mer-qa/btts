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
from gi.repository import GObject

_REASONABLE_TIMEOUT = 5000

class ProfileManager:
    class Error(Exception):
        pass

    class NoSuchProfileError(Error):
        def __init__(self, profile):
            ProfileManager.Error.__init__(self, "%s: No such profile" % (profile))
            self.profile = profile

    class TimeoutError(Error):
        def __init__(self):
            ProfileManager.Error.__init__(self, "Timeout")

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
            raise self.NoSuchProfileError(profile)

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
            raise self.TimeoutError()
        if self._job_result != "done":
            raise self.Error("Failed to start/stop system service %s: %s" %
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
