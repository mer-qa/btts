import dbus

import btts

class Adapter:
    def __init__(self):
        self.adapter_manager = btts.AdapterManager()
        name = self.adapter_manager.get_adapter_no_alias()

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
                self._properties_iface = dbus.Interface(self._adapter_object,
                                                        dbus.PROPERTIES_IFACE)
                break

    def _ensure_ready(self):
        if not self._adapter_object:
            raise AdapterManager.AdapterNotSetError()

    @property
    def path(self):
        self._ensure_ready()
        return self._adapter_object.object_path

    @property
    def powered(self):
        self._ensure_ready()
        return self._properties_iface.Get('org.bluez.Adapter1', 'Powered')

    @powered.setter
    def powered(self, powered):
        self._ensure_ready()
        return self._properties_iface.Set('org.bluez.Adapter1', 'Powered', powered)