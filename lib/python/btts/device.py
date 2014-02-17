import dbus
import re

import btts

class Device:
    class Error(Exception):
        pass

    class DeviceNotAvailableError(Error):
        pass

    def __init__(self):
        self._error = None
        self._path = None

        self._manager = btts.DeviceManager()
        self._adapter = btts.Adapter()

        self._device_object = None
        self._properties_iface = None

        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                 "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        for path, properties in objects.items():
            self._on_interfaces_added(path, properties)

        manager.connect_to_signal('InterfacesAdded', self._on_interfaces_added)
        manager.connect_to_signal('InterfacesRemoved', self._on_interfaces_removed)

    def _ensure_available(self):
        if self._error:
            raise self._error()
        if not self.available:
            raise self.DeviceNotAvailableError()

    @property
    def available(self):
        '''
        Is the device currently visible on the network?

        Exceptions:
            AdapterManager.AdapterNotSetError
            DeviceManager.DeviceNotSetError
        '''
        if self._error:
            raise self._error()
        return self._path is not None

    @btts.utils.signal
    def available_changed(self, available):
        pass

    @property
    def trusted(self):
        self._ensure_available()
        return self._properties_iface.Get('org.bluez.Device1', 'Trusted')

    @trusted.setter
    def trusted(self, trusted):
        self._ensure_available()
        return self._properties_iface.Set('org.bluez.Device1', 'Trusted', trusted)

    def remove(self):
        self._ensure_available()
        self._adapter._adapter_iface.RemoveDevice(self._path)

    @staticmethod
    def is_valid_address(address):
        return re.match('^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$', address) != None

    def _on_interfaces_added(self, object_path, interfaces_and_properties):
        if self.available:
            return
        try:
            if object_path.startswith(self._adapter.path):
                device_properties = interfaces_and_properties.get('org.bluez.Device1')
                if (device_properties is not None and
                        device_properties['Address'].lower() == self._manager.device_address):
                    self._path = object_path
                    bus = dbus.SystemBus()
                    self._device_object = bus.get_object('org.bluez', self._path)
                    self._properties_iface = dbus.Interface(self._device_object,
                                                            dbus.PROPERTIES_IFACE)
                    self.available_changed(True)
            self._error = None
        except (btts.DeviceManager.DeviceNotSetError,
                btts.AdapterManager.AdapterNotSetError) as e:
            self._error = type(e)

    def _on_interfaces_removed(self, object_path, interfaces):
        if object_path == self._path:
            self._path = None
            self.available_changed(False)
