%global pa_major   5.0
#global pa_minor   0

%global gitrel     20
%global gitcommit  a9351f1a7180cd7dce1eaae42a99e2e51d1fcfe1
%global shortcommit %(c=%{gitcommit}; echo ${c:0:6})

%ifarch %{ix86} x86_64 %{arm}
%global with_webrtc 1
%endif

# https://bugzilla.redhat.com/983606
%global _hardened_build 1

Name:           pulseaudio
Summary:        Improved Linux Sound Server
Version:        %{pa_major}%{?pa_minor:.%{pa_minor}}
Release:        2%{?gitcommit:.git%{shortcommit}}%{?dist}.btts1
License:        LGPLv2+
URL:            http://www.freedesktop.org/wiki/Software/PulseAudio
%if 0%{?gitrel}
# git clone git://anongit.freedesktop.org/pulseaudio/pulseaudio
# cd pulseaudio; git reset --hard %{gitcommit}; ./autogen.sh; make; make distcheck
Source0:        pulseaudio-%{version}-%{gitrel}-g%{shortcommit}.tar.xz
%else
Source0:        http://freedesktop.org/software/pulseaudio/releases/pulseaudio-%{version}.tar.xz
%endif
Source1:        default.pa-for-gdm

Patch3: 0001-bluetooth-disable-smoothing.patch

# jprvita's bluetooth-hf-audio-agent branch
Patch4: 0001-bluetooth-Fix-lines-going-over-collumn-128.patch
Patch5: 0002-bluetooth-Change-BlueZ-5-card-profile-name-from-a2dp.patch
Patch6: 0003-bluetooth-Add-basic-support-for-HEADSET-profiles.patch
Patch7: 0004-bluetooth-Add-BlueZ-5-headset-profile-names-in-polic.patch
Patch8: 0005-bluetooth-Create-Handsfree-Audio-Agent-NULL-backend.patch
Patch9: 0006-bluetooth-Create-Handsfree-Audio-Agent-oFono-backend.patch
Patch10: 0007-bluetooth-Monitor-D-Bus-signals.patch
Patch11: 0008-bluetooth-Create-pa_bluetooth_dbus_send_and_add_to_p.patch
Patch12: 0009-bluetooth-Register-Unregister-Handsfree-Audio-Agent-.patch
Patch13: 0010-bluetooth-List-HandsfreeAudioCard-objects-from-oFono.patch
Patch14: 0011-bluetooth-Parse-HandsfreeAudioCard-properties.patch
Patch15: 0012-bluetooth-Implement-transport-acquire-for-hf_audio_a.patch
Patch16: 0013-bluetooth-Implement-transport-release-for-hf_audio_a.patch
Patch17: 0014-bluetooth-Track-oFono-service.patch
Patch18: 0015-bluetooth-Handle-CardAdded-signal.patch
Patch19: 0016-bluetooth-Handle-CardRemoved-signal.patch
Patch20: 0017-bluetooth-Implement-org.ofono.HandsfreeAudioAgent.Re.patch
Patch21: 0018-bluetooth-Implement-org.ofono.HandsfreeAudioAgent.Ne.patch
Patch22: 0019-bluetooth-Rename-variable-to-improve-code-readabilit.patch
Patch23: 0020-bluetooth-Notify-the-main-thread-of-a-stream-fd-HUP.patch
Patch24: 0021-bluetooth-Suspend-the-source-sink-the-HFP-oFono-stre.patch

# jprvita's bluetooth-headsets-media-api branch
Patch25: 0022-bluetooth-Register-endpoints-for-SCO-based-profiles.patch

## upstream patches

BuildRequires:  m4
BuildRequires:  libtool-ltdl-devel
BuildRequires:  intltool
BuildRequires:  pkgconfig
BuildRequires:  doxygen
BuildRequires:  xmltoman
BuildRequires:  tcp_wrappers-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  libsndfile-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  glib2-devel
BuildRequires:  gtk2-devel
BuildRequires:  GConf2-devel
BuildRequires:  avahi-devel
%if 0%{?fedora}
%global enable_lirc 1
%global enable_jack 1
%endif
BuildRequires:  libatomic_ops-static, libatomic_ops-devel
%ifnarch s390 s390x
%if 0%{?fedora} > 19
%global bluez5 1
BuildRequires:  pkgconfig(bluez) >= 5.0
%else
%global bluez4 1
BuildRequires:  pkgconfig(bluez)
%endif
BuildRequires:  sbc-devel
%endif
BuildRequires:  libXt-devel
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  libXtst-devel
BuildRequires:  libXi-devel
BuildRequires:  libSM-devel
BuildRequires:  libX11-devel
BuildRequires:  libICE-devel
BuildRequires:  xcb-util-devel
BuildRequires:  openssl-devel
BuildRequires:  orc-devel
BuildRequires:  libtdb-devel
BuildRequires:  speex-devel >= 1.2
BuildRequires:  systemd-devel
BuildRequires:  libasyncns-devel
BuildRequires:  systemd-devel >= 184
BuildRequires:  json-c-devel
BuildRequires:  dbus-devel
BuildRequires:  libcap-devel
BuildRequires:  pkgconfig(fftw3f)
%if 0%{?with_webrtc}
BuildRequires:  webrtc-audio-processing-devel
%endif
# for --enable-tests
BuildRequires:  pkgconfig(check)

# retired along with -libs-zeroconf, add Obsoletes here for lack of anything better
Obsoletes:      padevchooser < 1.0
Requires(pre):  shadow-utils
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       systemd >= 184
Requires:       rtkit

%description
PulseAudio is a sound server for Linux and other Unix like operating
systems. It is intended to be an improved drop-in replacement for the
Enlightened Sound Daemon (ESOUND).

%package qpaeq
Summary:	Pulseaudio equalizer interface
Requires: 	%{name}%{?_isa} = %{version}-%{release}
Requires:	PyQt4
Requires:	dbus-python
%description qpaeq
qpaeq is a equalizer interface for pulseaudio's equalizer sinks.

%package esound-compat
Summary:        PulseAudio EsounD daemon compatibility script
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description esound-compat
A compatibility script that allows applications to call /usr/bin/esd
and start PulseAudio with EsounD protocol modules.

%if 0%{?enable_lirc}
%package module-lirc
Summary:        LIRC support for the PulseAudio sound server
BuildRequires:  lirc-devel
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description module-lirc
LIRC volume control module for the PulseAudio sound server.
%endif

%package module-x11
Summary:        X11 support for the PulseAudio sound server
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-utils

%description module-x11
X11 bell and security modules for the PulseAudio sound server.

%package module-zeroconf
Summary:        Zeroconf support for the PulseAudio sound server
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-utils

%description module-zeroconf
Zeroconf publishing module for the PulseAudio sound server.

%package module-bluetooth
Summary:        Bluetooth support for the PulseAudio sound server
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       bluez%{?bluez5: >= 5.0}

%description module-bluetooth
Contains Bluetooth audio (A2DP/HSP/HFP) support for the PulseAudio sound server.

%if 0%{?enable_jack}
%package module-jack
Summary:        JACK support for the PulseAudio sound server
BuildRequires:  jack-audio-connection-kit-devel
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description module-jack
JACK sink and source modules for the PulseAudio sound server.
%endif

%package module-gconf
Summary:        GConf support for the PulseAudio sound server
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description module-gconf
GConf configuration backend for the PulseAudio sound server.

%package libs
Summary:        Libraries for PulseAudio clients
License:        LGPLv2+
Obsoletes:      pulseaudio-libs-zeroconf < 1.1

%description libs
This package contains the runtime libraries for any application that wishes
to interface with a PulseAudio sound server.

%package libs-glib2
Summary:        GLIB 2.x bindings for PulseAudio clients
License:        LGPLv2+
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description libs-glib2
This package contains bindings to integrate the PulseAudio client library with
a GLIB 2.x based application.

%package libs-devel
Summary:        Headers and libraries for PulseAudio client development
License:        LGPLv2+
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs-glib2%{?_isa} = %{version}-%{release}
%description libs-devel
Headers and libraries for developing applications that can communicate with
a PulseAudio sound server.

%package utils
Summary:        PulseAudio sound server utilities
License:        LGPLv2+
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
# when made non-multilib'd, https://bugzilla.redhat.com/891425
Obsoletes:      pulseaudio-utils < 3.0-3

%description utils
This package contains command line utilities for the PulseAudio sound server.

%package gdm-hooks
Summary:        PulseAudio GDM integration
License:        LGPLv2+
Requires:       gdm >= 1:2.22.0
# for the gdm user
Requires(pre):  gdm

%description gdm-hooks
This package contains GDM integration hooks for the PulseAudio sound server.

%prep
%setup -q -T -b0 -n %{name}-%{version}%{?gitrel:-%{gitrel}-g%{shortcommit}}

%patch3 -p1 -b .disable_smoothing

%patch4  -p1 -b .0001-bluetooth-Fix-lines-going-over-collumn-128
%patch5  -p1 -b .0002-bluetooth-Change-BlueZ-5-card-profile-name-from-a2dp
%patch6  -p1 -b .0003-bluetooth-Add-basic-support-for-HEADSET-profiles
%patch7  -p1 -b .0004-bluetooth-Add-BlueZ-5-headset-profile-names-in-polic
%patch8  -p1 -b .0005-bluetooth-Create-Handsfree-Audio-Agent-NULL-backend
%patch9  -p1 -b .0006-bluetooth-Create-Handsfree-Audio-Agent-oFono-backend
%patch10 -p1 -b .0007-bluetooth-Monitor-D-Bus-signals
%patch11 -p1 -b .0008-bluetooth-Create-pa_bluetooth_dbus_send_and_add_to_p
%patch12 -p1 -b .0009-bluetooth-Register-Unregister-Handsfree-Audio-Agent-
%patch13 -p1 -b .0010-bluetooth-List-HandsfreeAudioCard-objects-from-oFono
%patch14 -p1 -b .0011-bluetooth-Parse-HandsfreeAudioCard-properties
%patch15 -p1 -b .0012-bluetooth-Implement-transport-acquire-for-hf_audio_a
%patch16 -p1 -b .0013-bluetooth-Implement-transport-release-for-hf_audio_a
%patch17 -p1 -b .0014-bluetooth-Track-oFono-service
%patch18 -p1 -b .0015-bluetooth-Handle-CardAdded-signal
%patch19 -p1 -b .0016-bluetooth-Handle-CardRemoved-signal
%patch20 -p1 -b .0017-bluetooth-Implement-org.ofono.HandsfreeAudioAgent.Re
%patch21 -p1 -b .0018-bluetooth-Implement-org.ofono.HandsfreeAudioAgent.Ne
%patch22 -p1 -b .0019-bluetooth-Rename-variable-to-improve-code-readabilit
%patch23 -p1 -b .0020-bluetooth-Notify-the-main-thread-of-a-stream-fd-HUP
%patch24 -p1 -b .0021-bluetooth-Suspend-the-source-sink-the-HFP-oFono-stre
%patch25 -p1 -b .0022-bluetooth-Register-endpoints-for-SCO-based-profiles

sed -i.no_consolekit -e \
  's/^load-module module-console-kit/#load-module module-console-kit/' \
  src/daemon/default.pa.in

NOCONFIGURE=1 ./bootstrap.sh

%if 0%{?gitrel:1}
# fixup PACKAGE_VERSION that leaks into pkgconfig files and friends
sed -i.PACKAGE_VERSION -e "s|^PACKAGE_VERSION=.*|PACKAGE_VERSION=\'%{version}\'|" configure
%else
## kill rpaths
%if "%{_libdir}" != "/usr/lib"
sed -i -e 's|"/lib /usr/lib|"/%{_lib} %{_libdir}|' configure
%endif
%endif

%build

%configure \
  --disable-static \
  --disable-rpath \
  --with-system-user=pulse \
  --with-system-group=pulse \
  --with-access-group=pulse-access \
  --disable-oss-output \
  %{?enable_jack:--enable-jack}%{!?enable_jack:--disable-jack} \
  %{?enable_lirc:--enable-lirc}%{!?enable_lirc:--disable-lirc} \
  %{?bluez4:--enable-bluez4}%{!?bluez4:--disable-bluez4} \
  %{?bluez5:--enable-bluez5}%{!?bluez5:--disable-bluez5} \
  --with-bluetooth-headset-backend=ofono \
%ifarch %{arm}
  --disable-neon-opt \
%endif
  --enable-systemd \
%if 0%{?with_webrtc}
  --enable-webrtc-aec \
%endif
  --enable-tests

# we really should preopen here --preopen-mods=module-udev-detect.la, --force-preopen
make %{?_smp_mflags} V=1
make doxygen

%install
make install DESTDIR=$RPM_BUILD_ROOT

# upstream should use udev.pc
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/udev/rules.d
mv -fv $RPM_BUILD_ROOT/lib/udev/rules.d/90-pulseaudio.rules $RPM_BUILD_ROOT%{_prefix}/lib/udev/rules.d

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/pulse
install -p -m644 -D %{SOURCE1} $RPM_BUILD_ROOT%{_localstatedir}/lib/gdm/.pulse/default.pa

## unpackaged files
# extraneous libtool crud
rm -fv $RPM_BUILD_ROOT%{_libdir}/*.la $RPM_BUILD_ROOT%{_libdir}/pulse-%{pa_major}/modules/*.la
# PA_MODULE_DEPRECATED("Please use module-udev-detect instead of module-detect!");
rm -fv $RPM_BUILD_ROOT%{_libdir}/pulse-%{pa_major}/modules/module-detect.so
# x11_device_manager folds -kde functionality into single -x11 autostart, so this
# one is no longer needed
rm -fv $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/pulseaudio-kde.desktop

%find_lang %{name}


%check
# Remove ifnarch when rhbz 1067470 is fixed:
%ifnarch ppc %{power64}
make check
%endif


%pre
getent group pulse-access >/dev/null || groupadd -r pulse-access
getent group pulse-access >/dev/null || groupadd -r pulse-rt
getent group pulse >/dev/null || groupadd -f -g 171 -r pulse
if ! getent passwd pulse >/dev/null ; then
    if ! getent passwd 171 >/dev/null ; then
      useradd -r -u 171 -g pulse -d /var/run/pulse -s /sbin/nologin -c "PulseAudio System Daemon" pulse
    else
      useradd -r -g pulse -d /var/run/pulse -s /sbin/nologin -c "PulseAudio System Daemon" pulse
    fi
fi
exit 0

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%posttrans
# handle renamed module-cork-music-on-phone => module-role-cork
(grep '^load-module module-cork-music-on-phone$' %{_sysconfdir}/pulse/default.pa > /dev/null && \
 sed -i.rpmsave -e 's|^load-module module-cork-music-on-phone$|load-module module-role-cork|' \
 %{_sysconfdir}/pulse/default.pa
) ||:

%files
%doc README LICENSE GPL LGPL
%dir %{_sysconfdir}/pulse/
%config(noreplace) %{_sysconfdir}/pulse/daemon.conf
%config(noreplace) %{_sysconfdir}/pulse/default.pa
%config(noreplace) %{_sysconfdir}/pulse/system.pa
%{_sysconfdir}/dbus-1/system.d/pulseaudio-system.conf
%dir %{_sysconfdir}/bash_completion.d/
%{_sysconfdir}/bash_completion.d/pulseaudio-bash-completion.sh
%{_bindir}/pulseaudio
%{_libdir}/libpulsecore-%{pa_major}.so
%dir %{_libdir}/pulse-%{pa_major}/
%dir %{_libdir}/pulse-%{pa_major}/modules/
%{_libdir}/pulse-%{pa_major}/modules/libalsa-util.so
%{_libdir}/pulse-%{pa_major}/modules/libcli.so
%{_libdir}/pulse-%{pa_major}/modules/libprotocol-cli.so
%{_libdir}/pulse-%{pa_major}/modules/libprotocol-esound.so
%{_libdir}/pulse-%{pa_major}/modules/libprotocol-http.so
%{_libdir}/pulse-%{pa_major}/modules/libprotocol-native.so
%{_libdir}/pulse-%{pa_major}/modules/libprotocol-simple.so
%{_libdir}/pulse-%{pa_major}/modules/librtp.so
%if 0%{?with_webrtc}
%{_libdir}/pulse-%{pa_major}/modules/libwebrtc-util.so
%endif
%{_libdir}/pulse-%{pa_major}/modules/module-alsa-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-alsa-source.so
%{_libdir}/pulse-%{pa_major}/modules/module-alsa-card.so
%{_libdir}/pulse-%{pa_major}/modules/module-cli-protocol-tcp.so
%{_libdir}/pulse-%{pa_major}/modules/module-cli-protocol-unix.so
%{_libdir}/pulse-%{pa_major}/modules/module-cli.so
%{_libdir}/pulse-%{pa_major}/modules/module-combine.so
%{_libdir}/pulse-%{pa_major}/modules/module-combine-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-dbus-protocol.so
%{_libdir}/pulse-%{pa_major}/modules/module-filter-apply.so
%{_libdir}/pulse-%{pa_major}/modules/module-filter-heuristics.so
%{_libdir}/pulse-%{pa_major}/modules/module-device-manager.so
%{_libdir}/pulse-%{pa_major}/modules/module-loopback.so
%{_libdir}/pulse-%{pa_major}/modules/module-esound-compat-spawnfd.so
%{_libdir}/pulse-%{pa_major}/modules/module-esound-compat-spawnpid.so
%{_libdir}/pulse-%{pa_major}/modules/module-esound-protocol-tcp.so
%{_libdir}/pulse-%{pa_major}/modules/module-esound-protocol-unix.so
%{_libdir}/pulse-%{pa_major}/modules/module-esound-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-udev-detect.so
%{_libdir}/pulse-%{pa_major}/modules/module-hal-detect.so
%{_libdir}/pulse-%{pa_major}/modules/module-http-protocol-tcp.so
%{_libdir}/pulse-%{pa_major}/modules/module-http-protocol-unix.so
%{_libdir}/pulse-%{pa_major}/modules/module-match.so
%{_libdir}/pulse-%{pa_major}/modules/module-mmkbd-evdev.so
%{_libdir}/pulse-%{pa_major}/modules/module-native-protocol-fd.so
%{_libdir}/pulse-%{pa_major}/modules/module-native-protocol-tcp.so
%{_libdir}/pulse-%{pa_major}/modules/module-native-protocol-unix.so
%{_libdir}/pulse-%{pa_major}/modules/module-null-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-null-source.so
%{_libdir}/pulse-%{pa_major}/modules/module-pipe-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-pipe-source.so
%{_libdir}/pulse-%{pa_major}/modules/module-remap-source.so
%{_libdir}/pulse-%{pa_major}/modules/module-rescue-streams.so
%{_libdir}/pulse-%{pa_major}/modules/module-role-ducking.so
%{_libdir}/pulse-%{pa_major}/modules/module-rtp-recv.so
%{_libdir}/pulse-%{pa_major}/modules/module-rtp-send.so
%{_libdir}/pulse-%{pa_major}/modules/module-simple-protocol-tcp.so
%{_libdir}/pulse-%{pa_major}/modules/module-simple-protocol-unix.so
%{_libdir}/pulse-%{pa_major}/modules/module-sine.so
%{_libdir}/pulse-%{pa_major}/modules/module-switch-on-port-available.so
%{_libdir}/pulse-%{pa_major}/modules/module-systemd-login.so
%{_libdir}/pulse-%{pa_major}/modules/module-tunnel-sink-new.so
%{_libdir}/pulse-%{pa_major}/modules/module-tunnel-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-tunnel-source-new.so
%{_libdir}/pulse-%{pa_major}/modules/module-tunnel-source.so
%{_libdir}/pulse-%{pa_major}/modules/module-volume-restore.so
%{_libdir}/pulse-%{pa_major}/modules/module-suspend-on-idle.so
%{_libdir}/pulse-%{pa_major}/modules/module-default-device-restore.so
%{_libdir}/pulse-%{pa_major}/modules/module-device-restore.so
%{_libdir}/pulse-%{pa_major}/modules/module-stream-restore.so
%{_libdir}/pulse-%{pa_major}/modules/module-card-restore.so
%{_libdir}/pulse-%{pa_major}/modules/module-ladspa-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-remap-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-always-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-console-kit.so
%{_libdir}/pulse-%{pa_major}/modules/module-position-event-sounds.so
%{_libdir}/pulse-%{pa_major}/modules/module-augment-properties.so
%{_libdir}/pulse-%{pa_major}/modules/module-role-cork.so
%{_libdir}/pulse-%{pa_major}/modules/module-sine-source.so
%{_libdir}/pulse-%{pa_major}/modules/module-intended-roles.so
%{_libdir}/pulse-%{pa_major}/modules/module-rygel-media-server.so
%{_libdir}/pulse-%{pa_major}/modules/module-echo-cancel.so
%{_libdir}/pulse-%{pa_major}/modules/module-switch-on-connect.so
%{_libdir}/pulse-%{pa_major}/modules/module-virtual-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-virtual-source.so
%{_libdir}/pulse-%{pa_major}/modules/module-virtual-surround-sink.so
%dir %{_datadir}/pulseaudio/
%dir %{_datadir}/pulseaudio/alsa-mixer/
%{_datadir}/pulseaudio/alsa-mixer/paths/
%{_datadir}/pulseaudio/alsa-mixer/profile-sets/
%{_mandir}/man1/pulseaudio.1*
%{_mandir}/man5/default.pa.5*
%{_mandir}/man5/pulse-cli-syntax.5*
%{_mandir}/man5/pulse-client.conf.5*
%{_mandir}/man5/pulse-daemon.conf.5*
%{_prefix}/lib/udev/rules.d/90-pulseaudio.rules
%dir %{_libexecdir}/pulse
%attr(0700, pulse, pulse) %dir %{_localstatedir}/lib/pulse

%files qpaeq
%{_bindir}/qpaeq
%{_libdir}/pulse-%{pa_major}/modules/module-equalizer-sink.so

%files esound-compat
%{_bindir}/esdcompat
%{_mandir}/man1/esdcompat.1.gz

%if 0%{?enable_lirc}
%files module-lirc
%{_libdir}/pulse-%{pa_major}/modules/module-lirc.so
%endif

%files module-x11
%{_sysconfdir}/xdg/autostart/pulseaudio.desktop
## no longer included per x11_device_manager.patch
#config %{_sysconfdir}/xdg/autostart/pulseaudio-kde.desktop
%{_bindir}/start-pulseaudio-x11
%{_libdir}/pulse-%{pa_major}/modules/module-x11-bell.so
%{_libdir}/pulse-%{pa_major}/modules/module-x11-publish.so
%{_libdir}/pulse-%{pa_major}/modules/module-x11-xsmp.so
%{_libdir}/pulse-%{pa_major}/modules/module-x11-cork-request.so
%{_mandir}/man1/start-pulseaudio-x11.1.gz

%files module-zeroconf
%{_libdir}/pulse-%{pa_major}/modules/libavahi-wrap.so
%{_libdir}/pulse-%{pa_major}/modules/module-zeroconf-publish.so
%{_libdir}/pulse-%{pa_major}/modules/module-zeroconf-discover.so
%{_libdir}/pulse-%{pa_major}/modules/libraop.so
%{_libdir}/pulse-%{pa_major}/modules/module-raop-discover.so
%{_libdir}/pulse-%{pa_major}/modules/module-raop-sink.so

%if 0%{?enable_jack}
%files module-jack
%{_libdir}/pulse-%{pa_major}/modules/module-jackdbus-detect.so
%{_libdir}/pulse-%{pa_major}/modules/module-jack-sink.so
%{_libdir}/pulse-%{pa_major}/modules/module-jack-source.so
%endif

%if 0%{?bluez4} || 0%{?bluez5}
%files module-bluetooth
%{_libdir}/pulse-%{pa_major}/modules/libbluez*-util.so
%{_libdir}/pulse-%{pa_major}/modules/module-bluez*-device.so
%{_libdir}/pulse-%{pa_major}/modules/module-bluez*-discover.so
%{_libdir}/pulse-%{pa_major}/modules/module-bluetooth-discover.so
%{_libdir}/pulse-%{pa_major}/modules/module-bluetooth-policy.so
%endif

%files module-gconf
%{_libdir}/pulse-%{pa_major}/modules/module-gconf.so
%{_libexecdir}/pulse/gconf-helper

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files libs -f %{name}.lang
%doc README LICENSE GPL LGPL
%dir %{_sysconfdir}/pulse/
%config(noreplace) %{_sysconfdir}/pulse/client.conf
%{_libdir}/libpulse.so.0*
%{_libdir}/libpulse-simple.so.0*
%dir %{_libdir}/pulseaudio/
%{_libdir}/pulseaudio/libpulsecommon-%{pa_major}.*
%{_libdir}/pulseaudio/libpulsedsp.*

%post libs-glib2 -p /sbin/ldconfig
%postun libs-glib2 -p /sbin/ldconfig

%files libs-glib2
%{_libdir}/libpulse-mainloop-glib.so.0*

%files libs-devel
%doc doxygen/html
%{_includedir}/pulse/
%{_libdir}/libpulse.so
%{_libdir}/libpulse-mainloop-glib.so
%{_libdir}/libpulse-simple.so
%{_libdir}/pkgconfig/libpulse*.pc
%dir %{_datadir}/vala
%dir %{_datadir}/vala/vapi
%{_datadir}/vala/vapi/libpulse.vapi
%{_datadir}/vala/vapi/libpulse.deps
%{_datadir}/vala/vapi/libpulse-mainloop-glib.vapi
%{_datadir}/vala/vapi/libpulse-mainloop-glib.deps
%dir %{_libdir}/cmake
%{_libdir}/cmake/PulseAudio/

%files utils
%{_bindir}/pacat
%{_bindir}/pacmd
%{_bindir}/pactl
%{_bindir}/paplay
%{_bindir}/parec
%{_bindir}/pamon
%{_bindir}/parecord
%{_bindir}/pax11publish
%{_bindir}/padsp
%{_bindir}/pasuspender
%{_mandir}/man1/pacat.1.gz
%{_mandir}/man1/pacmd.1.gz
%{_mandir}/man1/pactl.1.gz
%{_mandir}/man1/paplay.1.gz
%{_mandir}/man1/pasuspender.1.gz
%{_mandir}/man1/padsp.1.gz
%{_mandir}/man1/pax11publish.1.gz

%files gdm-hooks
%attr(0700, gdm, gdm) %dir %{_localstatedir}/lib/gdm/.pulse
%attr(0600, gdm, gdm) %{_localstatedir}/lib/gdm/.pulse/default.pa

%changelog
* Tue Mar 11 2014 Rex Dieter <rdieter@fedoraproject.org> 5.0-2
- drop Requires: kernel (per recent -devel ml thread)

* Tue Mar 04 2014 Rex Dieter <rdieter@fedoraproject.org> 5.0-1
- 5.0 (#1072259)

* Wed Feb 26 2014 Karsten Hopp <karsten@redhat.com> 4.99.4-3
- disable make check on PPC* (rhbz #1067470)

* Mon Feb 17 2014 Rex Dieter <rdieter@fedoraproject.org> 4.99.4-2
- -qpaeq subpkg (#1002585)

* Sat Feb 15 2014 Rex Dieter <rdieter@fedoraproject.org> 4.99.4-1
- 4.99.4

* Wed Jan 29 2014 Rex Dieter <rdieter@fedoraproject.org> 4.99.3-1
- 4.99.3

* Mon Jan 27 2014 Wim Taymans <wtaymans@redhat.com> - 4.99.2-2
- don't mark .desktop and dbus configurations as %config

* Fri Jan 24 2014 Rex Dieter <rdieter@fedoraproject.org> - 4.99.2-1
- 4.99.2 (#1057528)

* Wed Jan 22 2014 Wim Taymans <wtaymans@redhat.com> - 4.0-12.gitf81e3
- Use the statically allocated UID and GID from /usr/share/doc/setup/uidgid (#1056656)
- The pulse-rt group doesn't exist (#885020)

* Wed Jan 22 2014 Rex Dieter <rdieter@fedoraproject.org> - 4.0-11.gitf81e3
- handle jack/lirc modules better (#1056619)
- -libs-devel: own some dirs to avoid deps on cmake/vala
- -module-bluetooth: make dep arch'd for consistency

* Fri Jan 10 2014 Rex Dieter <rdieter@fedoraproject.org> - 4.0-10.gitf81e3
- enable hardened build (#983606)

* Sat Dec 07 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.0-9.gitf81e3
- X-KDE-autostart-phase=1

* Wed Oct 30 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.0-8.gitf81e3
- fix PACKAGE_VERSION

* Mon Oct 14 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.0-7.gitf81e3
- %%build fix typo, explicitly --enable-tests

* Mon Oct 14 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.0-6.gitf81e3 
- ship a single autostart file

* Fri Oct 11 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.0-5.gitf81e3
- fresh snapshot

* Mon Sep 23 2013 Kalev Lember <kalevlember@gmail.com> - 4.0-4.gita89ca
- Update to today's git snapshot
- Backport a patch for pulseaudio crash at startup (#1000966)

* Thu Aug 15 2013 Kalev Lember <kalevlember@gmail.com> - 4.0-3.gitbf9b3
- Update to git snapshot bf9b3f0 for BlueZ 5 support

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun  4 2013 Peter Robinson <pbrobinson@fedoraproject.org> 4.0-1
- New 4.0 stable release
- http://www.freedesktop.org/wiki/Software/PulseAudio/Notes/4.0/

* Thu May 30 2013 Rex Dieter <rdieter@fedoraproject.org> 3.99.2-2
- [RFE] Build with libcap (#969232)

* Sun May 26 2013 Peter Robinson <pbrobinson@fedoraproject.org> 3.99.2-1
- pulseaudio-3.99.2 (#966631)

* Fri May 03 2013 Rex Dieter <rdieter@fedoraproject.org> 3.99.1-1
- pulseaudio-3.99.1 (#952594)
- RFE: Restore the pipe-sink and pipe-source modules (#958949)
- prune (pre 1.x) changelog

* Thu Apr 11 2013 Rex Dieter <rdieter@fedoraproject.org> 3.0-7
- pull a few more patches from upstream stable-3.x branch

* Fri Feb 08 2013 Rex Dieter <rdieter@fedoraproject.org> 3.0-6
- default.pa: fix for renamed modules (#908117)

* Sat Jan 19 2013 Ville Skyttä <ville.skytta@iki.fi> - 3.0-5
- Own the %%{_libdir}/pulseaudio dir.
- Fix bogus %%changelog dates.

* Fri Jan 04 2013 Rex Dieter <rdieter@fedoraproject.org> 3.0-4
- alsa-mixer: Fix the analog-output-speaker-always path

* Fri Jan 04 2013 Rex Dieter <rdieter@fedoraproject.org> 3.0-3
- move libpulsedsp plugin to -libs, avoids -utils multilib (#891425)

* Wed Dec 19 2012 Dan Horák <dan[at]danny.cz> 3.0-2
- SBC is needed only when BlueZ is used

* Tue Dec 18 2012 Rex Dieter <rdieter@fedoraproject.org> 3.0-1
- pulseaudio-3.0

* Tue Dec 11 2012 Peter Robinson <pbrobinson@fedoraproject.org> 2.99.3-1
- PulseAudio 2.99.3 (3.0 rc3)

* Wed Oct 10 2012 Dan Horák <dan[at]danny.cz> 2.1-4
- fix the with_webrtc condition

* Tue Oct 09 2012 Dan Horák <dan[at]danny.cz> 2.1-3
- webrtc-aec is x86 and ARM only for now

* Mon Oct 08 2012 Debarshi Ray <rishi@fedoraproject.org> 2.1-2
- Enable webrtc-aec

* Tue Sep 25 2012 Rex Dieter <rdieter@fedoraproject.org> 2.1-1
- pulseaudio-2.1

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jun 23 2012 Kalev Lember <kalevlember@gmail.com> - 2.0-3
- Move module-jackdbus-detect.so to -module-jack subpackage with the
  rest of the jack modules

* Mon Jun 04 2012 Kay Sievers <kay@redhat.com> - 2.0-2
- rebuild for libudev1

* Sat May 12 2012 Rex Dieter <rdieter@fedoraproject.org> 2.0-1
- pulseaudio-2.0

* Sat Apr 21 2012 Matthias Clasen <mclasen@redhat.com> - 1.1-9
- Don't load the ck module in gdm, either

* Tue Feb 28 2012 Bruno Wolff III <bruno@wolff.to> - 1.1-8
- Bring in Lennart's patch from f17
- Temporary fix for CK/systemd move (#794690)

* Tue Feb 28 2012 Bruno Wolff III <bruno@wolff.to> - 1.1-7
- Fix for building with gcc 4.7

* Mon Jan 23 2012 Dan Horák <dan@danny.cz> - 1.1-6
- rebuilt for json-c-0.9-4.fc17

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 13 2011 Adam Jackson <ajax@redhat.com> 1.1-4
- Fix RHEL build

* Tue Nov 22 2011 Rex Dieter <rdieter@fedoraproject.org> 1.1-3
- Obsoletes: padevchooser < 1.0

* Thu Nov 10 2011 Rex Dieter <rdieter@fedoraproject.org> 1.1-2
- -libs: Obsoletes: pulseaudio-libs-zeroconf
- use versioned Obsoletes/Provides
- tighten subpkg deps via %%_isa
- remove autoconf/libtool hackery

* Thu Nov  3 2011 Lennart Poettering <lpoetter@redhat.com> - 1.1-1
- New upstream release
