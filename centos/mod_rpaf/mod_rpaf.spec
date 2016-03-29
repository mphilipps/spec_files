Name:           mod_rpaf
Version:        0.9.0
Release:        1%{?dist}
Summary:        reverse proxy add forward

Group:          System Environment/Daemons
License:        Apache License 2.0
URL:            https://github.com/taladar/mod_rpaf
Source0:        https://github.com/taladar/mod_rpaf/archive/v0.9.0.tar.gz 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  httpd-devel
Requires:       httpd

%description
Sets REMOTE_ADDR, HTTPS, and HTTP_PORT to the values provided by an upstream proxy. Sets remoteip-proxy-ip-list field in r->notes table to list of proxy intermediaries.

%prep
%setup -q


%build
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/usr/lib64/httpd/modules/
make install DESTDIR=$RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%_libdir/httpd/modules/mod_rpaf.so


%changelog
* Tue Mar 29 2016 Maximilian Philipps <mphilipps@saltation.de> - 0.9.0-1
- first created
