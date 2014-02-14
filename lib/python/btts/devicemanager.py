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
