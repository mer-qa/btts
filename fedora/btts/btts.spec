Name:		btts
Version:	0.1.0
Release:	1%{?dist}.btts1
Summary:	Bluetooth Test Suite

Group:		System/Networking
License:	GPLv2
URL:		http://github.com/mer-qa/btts
Source0:	%{name}-%{version}.tar.gz
Source1:	btts-pulseaudio.service

Requires:	bluez
Requires:	ofono
Requires:	pulseaudio
Requires:	pulseaudio-module-bluetooth
Requires:	pulseaudio-utils
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

%{__install} -m 0664 %{SOURCE1} %{buildroot}%{_unitdir}/

%files
%doc README
%{_bindir}/btts
%{_libexecdir}/%{name}/*
%{_unitdir}/*.service
%{_unitdir}/btts.target
%{_sysconfdir}/dbus-1/system.d/*.conf


%pre
getent group btts >/dev/null || groupadd --system btts
getent passwd btts >/dev/null || \
    useradd --base-dir /var/lib --comment "BlueTooth Test Suite" \
        --create-home --system --user-group btts
exit 0


%changelog
