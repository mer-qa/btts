Name:		echoprint-codegen
Version:	4.12
Release:	1%{?dist}.btts1
Summary:	Music Fingerprint and Resolving Framework
License:	MIT
URL:		https://github.com/echonest/echoprint-codegen
Source0:	https://github.com/echonest/echoprint-codegen/archive/v%{version}.tar.gz
Patch0:		0001-Fix-Makefile.patch
Patch1:		0002-Allow-uncompressed-output.patch
BuildRequires:	boost-devel
BuildRequires:	taglib-devel
BuildRequires:	zlib-devel
Requires:	ffmpeg


%description
Echoprint is an open source music fingerprint and resolving framework powered by
the The Echo Nest.

%package	devel
Summary:	Development files for %{name}
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description	devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1

%build
make %{?_smp_mflags} \
	BOOST_INCLUDEDIR=%{_includedir} \
	OPTFLAGS="%{optflags}" \
	-C src


%install
make install \
	DESTDIR=%{buildroot} \
	LIBDIR=%{_libdir} \
	INCLUDEDIR=%{_includedir} \
	BINDIR=%{_bindir} \
	OPTFLAGS="%{optflags}" \
	-C src



%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc AUTHORS LICENSE README.md
%{_libdir}/libcodegen.so.*
%{_bindir}/echoprint-codegen


%files devel
%{_includedir}/echoprint/
%{_libdir}/libcodegen.so



%changelog
# Initially based on http://oget.fedorapeople.org/review/echoprint-codegen.spec
