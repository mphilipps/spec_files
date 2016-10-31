Name:		darbackup
Version:	0.28
Release:	1%{?dist}
Summary:	darkbackup

Group:		System/Archive
License:	hoermann@saltation.de
URL:		http://www.saltation.de
Source:		https://gitlab.saltation.de/saltation-backup/darbackup/repository/archive.tar.gz?ref=master
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	bash
Requires:	bash >= 3.2 dar >= 2.4.8 grep >= 2.5.3 sed >= 4.1.5 gawk >= 3.1.5 time >= 1.7 openssh-client >= 5.1

%description
Wrapper for the dar backup tool that handles configuration files, scheduling policy, retention policy,...

%prep
%setup -q -n darbackup


%build


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a etc %{buildroot}
cp -a usr %{buildroot}



%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_sysconfdir}/*
%exclude %{_sysconfdir}/%{name}/darbackup.conf
%config(noreplace) %{_sysconfdir}/%{name}/darbackup.conf
%{_sbindir}/*

%changelog

