BIN_DIR          = $(DESTDIR)/usr/bin
LIBEXEC_DIR      = $(DESTDIR)/usr/libexec/btts
SYSTEMD_UNIT_DIR = $(DESTDIR)/usr/lib/systemd/system
DBUS_CONFIG_DIR  = $(DESTDIR)/etc/dbus-1/system.d

INSTALL_DIR	     = install --directory -m 0775
INSTALL_BIN_PROG     = install --target-directory="$(BIN_DIR)" -m 0775
INSTALL_LIBEXEC_PROG = install --target-directory="$(LIBEXEC_DIR)" -m 0775
INSTALL_SYSTEMD_UNIT = install --target-directory="$(SYSTEMD_UNIT_DIR)" -m 0664
INSTALL_DBUS_CONFIG  = install --target-directory="$(DBUS_CONFIG_DIR)" -m 0664

all:

install:
	$(INSTALL_DIR) $(BIN_DIR)
	$(INSTALL_BIN_PROG) src/btts

	$(INSTALL_DIR) $(LIBEXEC_DIR)
	$(INSTALL_LIBEXEC_PROG) src/btts_utils.py
	$(INSTALL_LIBEXEC_PROG) src/btts-bluez-agent
	$(INSTALL_LIBEXEC_PROG) src/btts-bluez-pairing-tool

	$(INSTALL_DIR) $(SYSTEMD_UNIT_DIR)
	$(INSTALL_SYSTEMD_UNIT) systemd/btts.target
	$(INSTALL_SYSTEMD_UNIT) systemd/btts-bluez-agent.service
	$(INSTALL_SYSTEMD_UNIT) systemd/btts-bluez-pairing-tool.service

	$(INSTALL_DIR) $(DBUS_CONFIG_DIR)
	$(INSTALL_DBUS_CONFIG) dbus/btts.conf
