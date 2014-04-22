Name:		btts
Version:	0.1.0
Release:	1%{?dist}.btts1
Summary:	Bluetooth Test Suite

Group:		System/Networking
License:	GPLv2
URL:		http://github.com/mer-qa/btts
Source0:	%{name}-%{version}.tar.gz

Requires:	bluez
Requires:	dconf
Requires:	echoprint-codegen
Requires:	ofono
Requires:	pulseaudio
Requires:	pulseaudio-module-bluetooth
Requires:	pulseaudio-utils
Requires:	python3
Requires:	python3-dbus
Requires:	python3-gobject
Requires:	sox
Requires:	minimodem
BuildRequires:	python2-devel
Requires(pre): shadow-utils

%global __python %{__python2}

%description
%{summary}.


%package rpc-server
Summary:  Bluetooth Test Suite - RPC Server
Group:    System/Networking
Requires: %{name} = %{version}-%{release}
Requires: openssh-server

%description rpc-server
Bluetooth Test Suite - RPC Server.


%package rpc-client
Summary:  Bluetooth Test Suite - RPC Client
Group:    System/Networking
Requires: openssh-clients

%description rpc-client
Bluetooth Test Suite - RPC Client.


%prep
%setup -q


%build
#%%configure
make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot}

%files
%doc README
%{_bindir}/btts
%{_exec_prefix}/lib/tmpfiles.d/btts.conf
%{_exec_prefix}/lib/btts/*
%{_libexecdir}/%{name}/btts-*
%{_libexecdir}/%{name}/environment
%{_libexecdir}/%{name}/environment.sh
%{_datadir}/%{name}/*
%{_datadir}/glib-2.0/schemas/*
%{_unitdir}/btts-bluez-agent.service
%{_unitdir}/btts-bluez-pairing-tool.service
%{_unitdir}/btts-a2dp-tool.service
%{_unitdir}/btts-dbus.service
%{_unitdir}/btts-hfp-tool.service
%{_unitdir}/btts-opp-client-tool.service
%{_unitdir}/btts-pulseaudio.service
%{_unitdir}/btts.target
%config %{_sysconfdir}/dbus-1/system.d/btts.conf

%defattr(0664, btts, btts, 0755)
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/adapters

%files rpc-server
%{_libexecdir}/%{name}/rpc-shell
%{_exec_prefix}/lib/tmpfiles.d/btts-rpcd.conf
%{_unitdir}/btts-rpcd.service
%{_unitdir}/btts-rpcdgenkeys.service
%defattr(0664, btts, btts, 0755)
%dir %{_sysconfdir}/%{name}/rpc
%config(noreplace) %attr(0600, btts, btts) %{_sysconfdir}/%{name}/rpc/authorized_keys
%config(noreplace) %{_sysconfdir}/%{name}/rpc/sshd_config

%files rpc-client
%{_bindir}/bttsr
%config(noreplace) %{_sysconfdir}/bttsr/bttsr.conf
%config(noreplace) %{_sysconfdir}/bttsr/id_rsa


%pre
getent group btts >/dev/null || groupadd --system btts
getent passwd btts >/dev/null || \
    useradd --base-dir /var/lib --comment "BlueTooth Test Suite" \
        --create-home --system --user-group btts
exit 0


%post
systemd-tmpfiles --create btts.conf
systemctl enable $(systemctl list-unit-files |awk '$1 ~ "^btts" {print $1}')


%post rpc-server
systemd-tmpfiles --create btts-rpcd.conf
systemctl enable btts-rpcd.service


%postun
if [ $1 -eq 0 ] ; then
    /usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
fi


%posttrans
/usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :


%changelog
