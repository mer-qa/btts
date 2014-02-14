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
import fileinput
import glob
import os
import re
import warnings

from btts.device import Device

_GSETTINGS_SCHEMA = "org.merproject.btts"

class DeviceManager:
    class Error(Exception):
        pass

    class DeviceNotSetError(Error):
        def __init__(self):
            DeviceManager.Error.__init__(self, "Device not set")

    class InvalidAddressError(Error):
        def __init__(self, address):
            DeviceManager.Error.__init__(self, "%s: Not a valid address" % (address))
            self.address = address

    def __init__(self):
        self.settings = Gio.Settings.new(_GSETTINGS_SCHEMA)

    @property
    def device_address(self):
        address = self.settings.get_string("device").lower()
        if not address:
            raise self.DeviceNotSetError()
        return address

    @device_address.setter
    def device_address(self, address):
        if not Device.is_valid_address(address):
            raise InvalidAddressError(address)

        self.settings.set_string("device", address.lower())
