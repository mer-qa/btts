Name:		ofono
Summary:	Open Source Telephony
Version:	1.13
Release:	1%{?dist}.btts1
Group:		System/Networking
License:	GPLv2
URL:		http://ofono.org
Source0:	http://www.kernel.org/pub/linux/network/ofono/ofono-%{version}.tar.xz
#Source100:	ofono.yaml
BuildRequires:	gcc-c++
BuildRequires:	libtool
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(libudev) >= 145
#BuildRequires:	pkgconfig(bluez) >= 4.99
BuildRequires:	pkgconfig(bluez)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(mobile-broadband-provider-info)
##Requires:	dbus-1
BuildRoot:  %{_tmppath}/%{name}-%{version}-build

%description
Description: %{summary}


%package devel
Summary:	Headers for oFono
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Description: %{summary}

%package test
Summary:	Test Scripts for oFono
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description test
Scripts for testing oFono and its functionality


%prep
%setup -q


%build
# to avoid "drivers/qmimodem/qmi.c:*: undefined reference to `__sync_sub_and_fetch_4'"
%if 0%{?fedora}
%ifarch i386 i486 i586
CFLAGS='-O2 -g -march=i586 -mtune=i686'
export CFLAGS
CXXFLAGS='-O2 -g -march=i586 -mtune=i686'
export CXXFLAGS
FFLAGS='-O2 -g -march=i586 -mtune=i686'
export FFLAGS
%endif
%endif
autoreconf --install
%configure \
	--disable-static \
	--enable-shared \
	--disable-debug \
	--enable-pie \
	--enable-threads \
	--enable-test \
	--enable-tools \
	--enable-dundee \
	--enable-udev \
	--enable-atmodem \
	--enable-cdmamodem \
	--enable-phonesim \
	--enable-isimodem \
	--enable-qmimodem \
	--enable-bluetooth \
	--enable-provision \
	--enable-datafiles
#make %{?jobs:-j%jobs}
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
%make_install


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc COPYING ChangeLog AUTHORS README
%doc /usr/share/man/man8/ofonod.8.gz
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/*
%{_sbindir}/*
#{_sysconfdir}/udev/rules.d/*
%{_unitdir}/*.service

%files devel
%defattr(-,root,root,-)
%{_includedir}/ofono/
%{_libdir}/pkgconfig/*.pc

%files test
%defattr(-,root,root,-)
%{_libdir}/%{name}/test/*

%changelog
