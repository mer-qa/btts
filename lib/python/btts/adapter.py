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
                self._adapter_iface = dbus.Interface(self._adapter_object,
                                                     'org.bluez.Adapter1')
                self._properties_iface = dbus.Interface(self._adapter_object,
                                                        dbus.PROPERTIES_IFACE)
                break

    def _ensure_ready(self):
        if not self._adapter_object:
            raise btts.AdapterManager.AdapterNotSetError()

    @property
    def path(self):
        self._ensure_ready()
        return self._adapter_object.object_path

    @property
    def address(self):
        self._ensure_ready()
        return self._properties_iface.Get('org.bluez.Adapter1', 'Address')

    @property
    def powered(self):
        self._ensure_ready()
        return self._properties_iface.Get('org.bluez.Adapter1', 'Powered')

    @powered.setter
    def powered(self, powered):
        self._ensure_ready()
        return self._properties_iface.Set('org.bluez.Adapter1', 'Powered', powered)

    @property
    def discovering(self):
        self._ensure_ready()
        return self._properties_iface.Get('org.bluez.Adapter1', 'Discovering')

    @discovering.setter
    def discovering(self, discovering):
        self._ensure_ready()
        if discovering:
            self._adapter_iface.StartDiscovery()
        else:
            # StopDiscovery() returns error when not discovering and the error is
            # not easily distinguishable from other failures -> not using
            # exceptions to handle this. OTOH sometimes bluez reports discovering
            # is on while it is not.
            if discovering != self.discovering:
                self._adapter_iface.StopDiscovery()

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

    @property
    def adapter_iface(self):
        self._ensure_ready()
        return self._adapter_iface

    @property
    def properties_iface(self):
        self._ensure_ready()
        return self._properties_iface
