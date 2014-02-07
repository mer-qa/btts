BIN_DIR          = $(DESTDIR)/usr/bin
LIBEXEC_DIR      = $(DESTDIR)/usr/libexec/btts
DATA_DIR         = $(DESTDIR)/usr/share/btts
CONF_DIR         = $(DESTDIR)/etc/btts
SYSTEMD_UNIT_DIR = $(DESTDIR)/usr/lib/systemd/system
TMPFILES_D_DIR   = $(DESTDIR)/usr/lib/tmpfiles.d
DBUS_CONFIG_DIR  = $(DESTDIR)/etc/dbus-1/system.d
PULSE_CONFIG_DIR = $(DATA_DIR)/pulse
PYTHON_PKG_DIR   = $(DESTDIR)/usr/lib/btts/python/btts
GSCHEMA_DIR      = $(DESTDIR)/usr/share/glib-2.0/schemas

INSTALL_DIR	     = install --directory -m 0775
INSTALL_BIN_PROG     = install --target-directory="$(BIN_DIR)" -m 0775
INSTALL_LIBEXEC_PROG = install --target-directory="$(LIBEXEC_DIR)" -m 0775
INSTALL_CONF_FILE    = install --target-directory="$(CONF_DIR)" -m 0664
INSTALL_SYSTEMD_UNIT = install --target-directory="$(SYSTEMD_UNIT_DIR)" -m 0664
INSTALL_TMPFILES_D_CONFIG = install --target-directory="$(TMPFILES_D_DIR)" -m 0664
INSTALL_DBUS_CONFIG  = install --target-directory="$(DBUS_CONFIG_DIR)" -m 0664
INSTALL_PULSE_CONFIG = install --target-directory="$(PULSE_CONFIG_DIR)" -m 0664
INSTALL_PYTHON_MOD   = install --target-directory="$(PYTHON_PKG_DIR)" -m 0664
INSTALL_GSCHEMA      = install --target-directory="$(GSCHEMA_DIR)" -m 0664

all:

install:
	$(INSTALL_DIR) $(BIN_DIR)
	$(INSTALL_BIN_PROG) src/btts

	$(INSTALL_DIR) $(LIBEXEC_DIR)
	$(INSTALL_LIBEXEC_PROG) src/environment
	$(INSTALL_LIBEXEC_PROG) src/environment.sh
	$(INSTALL_LIBEXEC_PROG) src/btts-adapter
	$(INSTALL_LIBEXEC_PROG) src/btts-agent
	$(INSTALL_LIBEXEC_PROG) src/btts-config
	$(INSTALL_LIBEXEC_PROG) src/btts-device
	$(INSTALL_LIBEXEC_PROG) src/btts-pairing

	$(INSTALL_DIR) $(PYTHON_PKG_DIR)
	$(INSTALL_PYTHON_MOD) lib/python/btts/__init__.py
	$(INSTALL_PYTHON_MOD) lib/python/btts/adapter.py
	$(INSTALL_PYTHON_MOD) lib/python/btts/adaptermanager.py
	$(INSTALL_PYTHON_MOD) lib/python/btts/cliutils.py
	$(INSTALL_PYTHON_MOD) lib/python/btts/device.py
	$(INSTALL_PYTHON_MOD) lib/python/btts/profilemanager.py
	$(INSTALL_PYTHON_MOD) lib/python/btts/utils.py

	$(INSTALL_DIR) $(CONF_DIR)
	$(INSTALL_CONF_FILE) conf/adapters

	$(INSTALL_DIR) $(SYSTEMD_UNIT_DIR)
	$(INSTALL_SYSTEMD_UNIT) systemd/btts.target
	$(INSTALL_SYSTEMD_UNIT) systemd/btts-dbus.service
	$(INSTALL_SYSTEMD_UNIT) systemd/btts-pulseaudio.service
	$(INSTALL_SYSTEMD_UNIT) systemd/btts-bluez-agent.service
	$(INSTALL_SYSTEMD_UNIT) systemd/btts-bluez-pairing-tool.service

	$(INSTALL_DIR) $(TMPFILES_D_DIR)
	$(INSTALL_TMPFILES_D_CONFIG) systemd/tmpfiles.d/btts.conf

	$(INSTALL_DIR) $(DBUS_CONFIG_DIR)
	$(INSTALL_DBUS_CONFIG) conf/dbus/btts.conf

	$(INSTALL_DIR) $(PULSE_CONFIG_DIR)
	$(INSTALL_PULSE_CONFIG) conf/pulse/default.pa

	$(INSTALL_DIR) $(GSCHEMA_DIR)
	$(INSTALL_GSCHEMA) conf/btts.gschema.xml
