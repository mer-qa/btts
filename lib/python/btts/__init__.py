__all__ = [
           # from adapter
           'Adapter',

           # from adaptermanager
           'AdapterManager',

           # from device
           'Device',

           # from devicemanager
           'DeviceManager',

           # from profilemanager
           'ProfileManager',
           ]

import sys

if sys.version_info.major > 2:
    import btts.cliutils

import btts.utils

from btts.adapter import Adapter
from btts.adaptermanager import AdapterManager
from btts.device import Device
from btts.devicemanager import DeviceManager
from btts.profilemanager import ProfileManager
