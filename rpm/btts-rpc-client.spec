Name:       btts-rpc-client
Summary:    Bluetooth Test Suite RPC Client
Version:    0.1.0
Release:    0
Group:      Development/Testing
License:    GPLv2
URL:        https://github.com/mer-qa/btts
Source0:    btts-%{version}.tar.gz
Requires:   openssh-clients

%description
This package contains the 'bttsr' tool from Bluetooth Test Suite


%prep
%setup -q -n btts-%{version}

%build

%install
rm -rf %{buildroot}

make install-rpc-client DESTDIR=%{buildroot} DEFAULT_BTTS_HOST=%{?btts_host}

%files
%defattr(-,root,root,-)
%{_bindir}/bttsr
%{_sysconfdir}/bttsr/bttsr.conf
%{_sysconfdir}/bttsr/id_rsa
