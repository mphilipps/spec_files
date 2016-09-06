Name:		tmux
Version:  2.2
Release:	2%{?dist}
Summary:	tmux

Group:		System Environment/Shells
License:	ISC
URL:		https://tmux.github.io/
Source:	https://github.com/%{name}/%{name}/releases/download/%{version}/%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	gcc ncurses-devel libevent-devel >= 2.0
Requires:	ncurses libevent

%description


%prep
%setup -q


%build
%configure
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc
%{_bindir}/tmux
%{_mandir}/man1/tmux.1.gz


%changelog

