Name:		btts
Version:	0.1.0
Release:	1%{?dist}
Summary:	Bluetooth Test Suite

Group:		System/Networking
License:	GPLv2
URL:		http://github.com/nemomobile/btts
Source0:	%{name}-%{version}.tar.gz

Requires:	bluez
Requires:	ofono
Requires:	pulseaudio
Requires:	pulseaudio-module-bluetooth
Requires:	pulseaudio-utils

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
%{_libexecdir}/%{name}/*
%{_unitdir}/*.service
%{_unitdir}/btts.target
%{_sysconfdir}/dbus-1/system.d/*.conf


%changelog
