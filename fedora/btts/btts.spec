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
Requires:	ofono
Requires:	pulseaudio
Requires:	pulseaudio-module-bluetooth
Requires:	pulseaudio-utils
Requires:	python3
Requires:	python3-dbus
Requires:	python3-gobject
BuildRequires:	python2-devel
Requires(pre): shadow-utils

%global __python %{__python2}

%description
Description: %{summary}

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
%{_exec_prefix}/lib/tmpfiles.d/*
%{_exec_prefix}/lib/btts/*
%{_libexecdir}/%{name}/*
%{_datadir}/%{name}/*
%{_datadir}/glib-2.0/schemas/*
%{_unitdir}/*
%config %{_sysconfdir}/dbus-1/system.d/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/adapters


%pre
getent group btts >/dev/null || groupadd --system btts
getent passwd btts >/dev/null || \
    useradd --base-dir /var/lib --comment "BlueTooth Test Suite" \
        --create-home --system --user-group btts
exit 0


%post
systemd-tmpfiles --create btts.conf
systemctl enable $(systemctl list-unit-files |awk '$1 ~ "^btts" {print $1}')


%postun
if [ $1 -eq 0 ] ; then
    /usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
fi


%posttrans
/usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :


%changelog
