import dbus

import btts

class Device:
    def __init__(self, address):
        self._address = address
        self._path = None

        self._adapter = btts.Adapter()

        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                 "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        for path, properties in objects.items():
            self._on_interfaces_added(path, properties)

        manager.connect_to_signal('InterfacesAdded', self._on_interfaces_added)
        manager.connect_to_signal('InterfacesRemoved', self._on_interfaces_removed)

    @property
    def address(self):
        return self._address

    @property
    def available(self):
        '''
        Is the device currently visible on the network?

        Exceptions:
            AdapterManager.AdapterNotSetError
        '''
        return self._path is not None

    @btts.utils.signal
    def available_changed(self, available):
        pass

    def _on_interfaces_added(self, object_path, interfaces_and_properties):
        if self.available:
            return
        try:
            if object_path.startswith(self._adapter.path):
                device_properties = interfaces_and_properties.get('org.bluez.Device1')
                if (device_properties is not None and
                        device_properties['Address'] == self._address):
                    self._path = object_path
                    self.available_changed(True)
        except btts.AdapterManager.AdapterNotSetError:
            pass

    def _on_interfaces_removed(self, object_path, interfaces):
        if not self.available:
            return
        if object_path == self._path:
            self._path = None
            self.available_changed(False)
