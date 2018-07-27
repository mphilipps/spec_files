Summary: Daemon to ban hosts that cause multiple authentication errors
Name: fail2ban
Version: 0.10.3.1
Release: 3%{?dist}
License: GPLv2+
URL: http://fail2ban.sourceforge.net/
Source0: https://github.com/%{name}/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
#Source0: https://github.com/sebres/%{name}/archive/f2b-perfom-prepare-716-cs.tar.gz#/%{name}-test.tar.gz
# Give up being PartOf iptables and ipset for now
# https://bugzilla.redhat.com/show_bug.cgi?id=1379141
# https://bugzilla.redhat.com/show_bug.cgi?id=1573185
Patch2: fail2ban-partof.patch

BuildRequires: python3-devel
BuildRequires: /usr/bin/2to3
# For testcases
BuildRequires: python3-inotify
BuildRequires: sqlite
BuildArch: noarch
%if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires: systemd
%endif
# Default components
Requires: %{name}-firewalld = %{version}-%{release}
Requires: %{name}-sendmail = %{version}-%{release}
Requires: %{name}-server = %{version}-%{release}
# Currently this breaks jails that don't log to the journal
#Requires: %{name}-systemd = %{version}-%{release}

%description
Fail2Ban scans log files and bans IP addresses that makes too many password
failures. It updates firewall rules to reject the IP address. These rules can
be defined by the user. Fail2Ban can read multiple log files such as sshd or
Apache web server ones.

Fail2Ban is able to reduce the rate of incorrect authentications attempts
however it cannot eliminate the risk that weak authentication presents.
Configure services to use only two factor or public/private authentication
mechanisms if you really want to protect services.

This is a meta-package that will install the default configuration.  Other
sub-packages are available to install support for other actions and
configurations.


%package server
Summary: Core server component for Fail2Ban
%if 0%{?fedora} || 0%{?rhel} >= 7
Requires: python3-systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires: initscripts
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
%endif
Requires: ipset
Requires: iptables

%description server
This package contains the core server components for Fail2Ban with minimal
dependencies.  You can install this directly if you want to have a small
installation and know what you are doing.


%package all
Summary: Install all Fail2Ban packages and dependencies
Requires: %{name}-firewalld = %{version}-%{release}
Requires: %{name}-hostsdeny = %{version}-%{release}
Requires: %{name}-mail = %{version}-%{release}
Requires: %{name}-sendmail = %{version}-%{release}
Requires: %{name}-server = %{version}-%{release}
Requires: %{name}-shorewall = %{version}-%{release}
# Currently this breaks jails that don't log to the journal
#Requires: %{name}-systemd = %{version}-%{release}
# No python3 support for gamin
#Requires: gamin-python
Requires: perl-interpreter
Requires: python3-inotify
Requires: /usr/bin/whois

%description all
This package installs all of the Fail2Ban packages and dependencies.


%package firewalld
Summary: Firewalld support for Fail2Ban
Requires: %{name}-server = %{version}-%{release}
Requires: firewalld

%description firewalld
This package enables support for manipulating firewalld rules.  This is the
default firewall service in Fedora.


%package hostsdeny
Summary: Hostsdeny (tcp_wrappers) support for Fail2Ban
Requires: %{name}-server = %{version}-%{release}
Requires: ed
Requires: tcp_wrappers

%description hostsdeny
This package enables support for manipulating tcp_wrapper's /etc/hosts.deny
files.


%package tests
Summary: Fail2Ban testcases
Requires: %{name}-server = %{version}-%{release}

%description tests
This package contains Fail2Ban's testscases and scripts.


%package mail
Summary: Mail actions for Fail2Ban
Requires: %{name}-server = %{version}-%{release}
Requires: mailx

%description mail
This package installs Fail2Ban's mail actions.  These are an alternative
to the default sendmail actions.


%package sendmail
Summary: Sendmail actions for Fail2Ban
Requires: %{name}-server = %{version}-%{release}
Requires: /usr/sbin/sendmail

%description sendmail
This package installs Fail2Ban's sendmail actions.  This is the default
mail actions for Fail2Ban.


%package shorewall
Summary: Shorewall support for Fail2Ban
Requires: %{name}-server = %{version}-%{release}
Requires: shorewall

%description shorewall
This package enables support for manipulating shorewall rules.


%package systemd
Summary: Systemd journal configuration for Fail2Ban
Requires: %{name}-server = %{version}-%{release}

%description systemd
This package configures Fail2Ban to use the systemd journal for its log input
by default.


%prep
%setup -q
%patch2 -p1 -b .partof
# Use Fedora paths
sed -i -e 's/^before = paths-.*/before = paths-fedora.conf/' config/jail.conf
2to3 --write --nobackups .
find -type f -exec sed -i -e '1s,^#!/usr/bin/python *,#!/usr/bin/python%{python3_version},' {} +

%build
%py3_build

%install
%py3_install

%if 0%{?fedora} || 0%{?rhel} >= 7
mkdir -p %{buildroot}%{_unitdir}
cp -p build/fail2ban.service %{buildroot}%{_unitdir}/
%else
mkdir -p %{buildroot}%{_initddir}
install -p -m 755 files/redhat-initd %{buildroot}%{_initddir}/fail2ban
%endif
mkdir -p %{buildroot}%{_mandir}/man{1,5}
install -p -m 644 man/*.1 %{buildroot}%{_mandir}/man1
install -p -m 644 man/*.5 %{buildroot}%{_mandir}/man5
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
install -p -m 644 files/fail2ban-logrotate %{buildroot}%{_sysconfdir}/logrotate.d/fail2ban
install -d -m 0755 %{buildroot}/run/fail2ban/
install -m 0600 /dev/null %{buildroot}/run/fail2ban/fail2ban.pid
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/fail2ban/
mkdir -p %{buildroot}%{_tmpfilesdir}
install -p -m 0644 files/fail2ban-tmpfiles.conf %{buildroot}%{_tmpfilesdir}/fail2ban.conf
# Remove non-Linux actions
rm %{buildroot}%{_sysconfdir}/%{name}/action.d/*ipfw.conf
rm %{buildroot}%{_sysconfdir}/%{name}/action.d/{ipfilter,pf,ufw}.conf
rm %{buildroot}%{_sysconfdir}/%{name}/action.d/osx-*.conf
# firewalld configuration
cat > %{buildroot}%{_sysconfdir}/%{name}/jail.d/00-firewalld.conf <<EOF
# This file is part of the fail2ban-firewalld package to configure the use of
# the firewalld actions as the default actions.  You can remove this package
# (along with the empty fail2ban meta-package) if you do not use firewalld
[DEFAULT]
banaction = firewallcmd-ipset
EOF
# systemd journal configuration
cat > %{buildroot}%{_sysconfdir}/%{name}/jail.d/00-systemd.conf <<EOF
# This file is part of the fail2ban-systemd package to configure the use of
# the systemd journal as the default backend.  You can remove this package
# (along with the empty fail2ban meta-package) if you do not want to use the
# journal backend
[DEFAULT]
backend=systemd
EOF
# Remove installed doc, use doc macro instead
rm -r %{buildroot}%{_docdir}/%{name}

%check
# Need a UTF-8 locale to work
export LANG=en_US.UTF-8
./fail2ban-testcases-all-python3 --no-network

%post server
%if 0%{?fedora} || 0%{?rhel} >= 7
%systemd_post fail2ban.service
%else
/sbin/chkconfig --add %{name}
%endif

%preun server
%if 0%{?fedora} || 0%{?rhel} >= 7
%systemd_preun fail2ban.service
%else
if [ $1 = 0 ]; then
  /sbin/service %{name} stop > /dev/null 2>&1
  /sbin/chkconfig --del %{name}
fi
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
%postun server
%systemd_postun_with_restart fail2ban.service
%endif

%files

%files server
%doc README.md TODO ChangeLog COPYING doc/*.txt
%{_bindir}/fail2ban-client
%{_bindir}/fail2ban-python
%{_bindir}/fail2ban-regex
%{_bindir}/fail2ban-server
%{python3_sitelib}/*
%exclude %{python3_sitelib}/fail2ban/tests
%if 0%{?fedora} || 0%{?rhel} >= 7
%{_unitdir}/fail2ban.service
%else
%{_initddir}/fail2ban
%endif
%{_mandir}/man1/fail2ban.1*
%{_mandir}/man1/fail2ban-client.1*
%{_mandir}/man1/fail2ban-python.1*
%{_mandir}/man1/fail2ban-regex.1*
%{_mandir}/man1/fail2ban-server.1*
%{_mandir}/man5/*.5*
%config(noreplace) %{_sysconfdir}/fail2ban
%exclude %{_sysconfdir}/fail2ban/action.d/complain.conf
%exclude %{_sysconfdir}/fail2ban/action.d/hostsdeny.conf
%exclude %{_sysconfdir}/fail2ban/action.d/mail-*.conf
%exclude %{_sysconfdir}/fail2ban/action.d/sendmail-*.conf
%exclude %{_sysconfdir}/fail2ban/action.d/shorewall.conf
%exclude %{_sysconfdir}/fail2ban/jail.d/*.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/fail2ban
%{_tmpfilesdir}/fail2ban.conf
%dir %{_localstatedir}/lib/fail2ban/
%dir /run/%{name}/
%ghost %verify(not size mtime md5) /run/%{name}/%{name}.pid

%files all

%files firewalld
%config(noreplace) %{_sysconfdir}/fail2ban/jail.d/00-firewalld.conf

%files hostsdeny
%config(noreplace) %{_sysconfdir}/fail2ban/action.d/hostsdeny.conf

%files tests
%{_bindir}/fail2ban-testcases
%{_mandir}/man1/fail2ban-testcases.1*
%{python3_sitelib}/fail2ban/tests

%files mail
%config(noreplace) %{_sysconfdir}/fail2ban/action.d/complain.conf
%config(noreplace) %{_sysconfdir}/fail2ban/action.d/mail-*.conf

%files sendmail
%config(noreplace) %{_sysconfdir}/fail2ban/action.d/sendmail-*.conf

%files shorewall
%config(noreplace) %{_sysconfdir}/fail2ban/action.d/shorewall.conf

%files systemd
%config(noreplace) %{_sysconfdir}/fail2ban/jail.d/00-systemd.conf


%changelog
* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Orion Poplawski <orion@nwra.com> - 0.10.3.1-2
- Remove PartOf ipset.service (bug #1573185)

* Tue Jun 19 2018 Orion Poplawski <orion@nwra.com> - 0.10.3.1-1
- Update to 0.10.3.1

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.10.2-2
- Rebuilt for Python 3.7

* Wed Mar 28 2018 Orion Poplawski <orion@nwra.com> - 0.10.2-1
- Update to 0.10.2

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Dec 30 2017 Orion Poplawski <orion@nwra.com> - 0.10.1-3
- Add upstream patch to fix ipset issue (bug #1525134)

* Sat Dec 30 2017 Orion Poplawski <orion@nwra.com> - 0.10.1-2
- Add upstream patch to fix buildroot issue

* Tue Nov 14 2017 Orion Poplawski <orion@cora.nwra.com> - 0.10.1-1
- Update to 0.10.1

* Wed Sep 20 2017 Orion Poplawski <orion@cora.nwra.com> - 0.10.0-1
- Update to 0.10.0

* Wed Aug 16 2017 Orion Poplawski <orion@cora.nwra.com> - 0.9.7-4
- Use BR /usr/bin/2to3

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 13 2017 Petr Pisar <ppisar@redhat.com> - 0.9.7-2
- perl dependency renamed to perl-interpreter
  <https://fedoraproject.org/wiki/Changes/perl_Package_to_Install_Core_Modules>

* Wed Jul 12 2017 Orion Poplawski <orion@cora.nwra.com> - 0.9.7-1
- Update to 0.9.7

* Wed Feb 15 2017 Orion Poplawski <orion@cora.nwra.com> - 0.9.6-4
- Properly handle /run/fail2ban (bug #1422500)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 10 2017 Orion Poplawski <orion@cora.nwra.com> - 0.9.6-2
- Add upstream patch to fix fail2ban-regex with journal

* Fri Jan 6 2017 Orion Poplawski <orion@cora.nwra.com> - 0.9.6-1
- Update to 0.9.6
- Fix sendmail-auth filter (bug #1329919)

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 0.9.5-5
- Rebuild for Python 3.6

* Fri Oct 7 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.5-4
- %%ghost /run/fail2ban
- Fix typo in shorewall description
- Move tests to -tests sub-package

* Mon Oct 3 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.5-3
- Add journalmatch entries for sendmail (bug #1329919)

* Mon Oct 3 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.5-2
- Give up being PartOf iptables to allow firewalld restarts to work
  (bug #1379141)

* Mon Oct 3 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.5-1
- Add patch to fix failing test

* Sun Sep 25 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.5-1
- Update to 0.9.5
- Drop mysql patch applied upstream

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.4-6
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Apr 5 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.4-5
- Fix python3 usage (bug #1324113)

* Sun Mar 27 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.4-4
- Use %%{_tmpfilesdir} for systemd tmpfile config

* Wed Mar 9 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.4-3
- No longer need to add After=firewalld.service (bug #1301910)

* Wed Mar 9 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.4-2
- Fix mariadb/mysql log handling

* Wed Mar 9 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.4-1
- Update to 0.9.4
- Use mariadb log path by default

* Tue Feb 23 2016 Orion Poplawski <orion@cora.nwra.com> - 0.9.3-3
- Use python3 (bug #1282498)

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Sep 12 2015 Orion Poplawski <orion@cora.nwra.com> - 0.9.3-1
- Update to 0.9.3
- Cleanup spec, use new python macros

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Apr 30 2015 Orion Poplawski <orion@cora.nwra.com> - 0.9.2-1
- Update to 0.9.2

* Mon Mar 16 2015 Orion Poplawski <orion@cora.nwra.com> - 0.9.1-4
- Do not load user paths for fail2ban-{client,server} (bug #1202151)

* Sun Feb 22 2015 Orion Poplawski <orion@cora.nwra.com> - 0.9.1-3
- Do not use systemd by default

* Fri Nov 28 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9.1-2
- Fix php-url-fopen logpath (bug #1169026)

* Tue Oct 28 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9.1-1
- Update to 0.9.1

* Fri Aug 15 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-8
- Add patch to fix tests

* Fri Aug 8 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-8
- Fix log paths for some jails (bug #1128152)

* Mon Jul 21 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-7
- Use systemd for EL7

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Mar 20 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-5
- Require mailx for /usr/bin/mail

* Thu Mar 20 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-4
- Need empty %%files to produce main and -all package

* Wed Mar 19 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-3
- Split into sub-packages for different components
- Enable journal filter by default (bug #985567)
- Enable firewalld action by default (bug #1046816)
- Add upstream patch to fix setting loglevel in fail2ban.conf
- Add upstream patches to fix tests in mock, run tests

* Tue Mar 18 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-2
- Use Fedora paths
- Start after firewalld (bug #1067147)

* Mon Mar 17 2014 Orion Poplawski <orion@cora.nwra.com> - 0.9-1
- Update to 0.9

* Tue Sep 24 2013 Orion Poplawski <orion@cora.nwra.com> - 0.9-0.3.git1f1a561
- Update to current 0.9 git branch
- Rebase init patch, drop jail.d and notmp patch applied upstream

* Fri Aug 9 2013 Orion Poplawski <orion@cora.nwra.com> - 0.9-0.2.gitd529151
- Ship jail.conf(5) man page
- Ship empty /etc/fail2ban/jail.d directory

* Thu Aug 8 2013 Orion Poplawski <orion@cora.nwra.com> - 0.9-0.1.gitd529151
- Update to 0.9 git branch
- Rebase patches
- Require systemd-python for journal support

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jun 12 2013 Orion Poplawski <orion@cora.nwra.com> - 0.8.10-1
- Update to 0.8.10 security release
- Use upstream provided systemd files
- Drop upstreamed patches, rebase log2syslog and notmp patches

* Fri Mar 15 2013 Orion Poplawski <orion@cora.nwra.com> - 0.8.8-4
- Use systemd init for Fedora 19+ (bug #883158)

* Thu Feb 14 2013 Orion Poplawski <orion@cora.nwra.com> - 0.8.8-3
- Add patch from upstream to fix module imports (Bug #892365)
- Add patch from upstream to UTF-8 characters in syslog (Bug #905097)
- Drop Requires: tcp_wrappers and shorewall (Bug #781341)

* Fri Jan 18 2013 Orion Poplawski <orion@cora.nwra.com> - 0.8.8-2
- Add patch to prevent sshd blocks of successful logins for systems that use
  sssd or ldap

* Mon Dec 17 2012 Orion Poplawski <orion@cora.nwra.com> - 0.8.8-1
- Update to 0.8.8 (CVE-2012-5642 Bug #887914)

* Thu Oct 11 2012 Orion Poplawski <orion@cora.nwra.com> - 0.8.7.1-1
- Update to 0.8.7.1
- Drop fd_cloexec, pyinotify, and examplemail patches fixed upstream
- Rebase sshd and notmp patches
- Use _initddir macro

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.4-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.4-28
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Apr  9 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.4-27
- Move tmp files to /var/lib (suggested by Phil Anderson).
- Enable inotify support (by Jonathan Underwood).
- Fixes RH bugs #669966, #669965, #551895, #552947, #658849, #656584.

* Sun Feb 14 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.4-24
- Patch by Jonathan G. Underwood <jonathan.underwood@gmail.com> to
  cloexec another fd leak.

* Fri Sep 11 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.4-23
- update to 0.8.4.

* Wed Sep  2 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.3-22
- Update to a newer svn snapshot to fix python 2.6 issue.

* Thu Aug 27 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.3-21
- Log to syslog (RH bug #491983). Also deals with RH bug #515116.
- Check inodes of log files (RH bug #503852).

* Sat Feb 14 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.3-18
- Fix CVE-2009-0362 (Fedora bugs #485461, #485464, #485465, #485466).

* Mon Dec 01 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.8.3-17
- Rebuild for Python 2.6

* Sun Aug 24 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.3-16
- Update to 0.8.3.

* Wed May 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.8.2-15
- fix license tag

* Thu Mar 27 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.2-14
- Close on exec fixes by Jonathan Underwood.

* Sun Mar 16 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.2-13
- Add %%{_localstatedir}/run/fail2ban (David Rees).

* Fri Mar 14 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.2-12
- Update to 0.8.2.

* Thu Jan 31 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 0.8.1-11
- Move socket file from /tmp to /var/run to prevent SElinux from stopping
  fail2ban from starting (BZ #429281)
- Change logic in init file to start with -x to remove the socket file in case
  of unclean shutdown

* Wed Aug 15 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.1-10
- Update to 0.8.1.
- Remove patch fixing CVE-2007-4321 (upstream).
- Remove AllowUsers patch (upstream).
- Add dependency to gamin-python.

* Thu Jun 21 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.0-9
- Fix remote log injection (no CVE assignment yet).

* Sun Jun  3 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.0-8
- Also trigger on non-AllowUsers failures (Jonathan Underwood
  <jonathan.underwood@gmail.com>).

* Wed May 23 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.0-7
- logrotate should restart fail2ban (Zing <zing@fastmail.fm>).
- send mail to root; logrotate (Jonathan Underwood
  <jonathan.underwood@gmail.com>)

* Sat May 19 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.8.0-4
- Update to 0.8.0.
- enable ssh by default, fix log file for ssh scanning, adjust python
  dependency (Jonathan Underwood <jonathan.underwood@gmail.com>)

* Sat Dec 30 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.6.2-3
- Remove forgotten condrestart.

* Fri Dec 29 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.6.2-2
- Move /usr/lib/fail2ban to %%{_datadir}/fail2ban.
- Don't default chkconfig to enabled.
- Add dependencies on service/chkconfig.
- Use example iptables/ssh config as default config.

* Mon Dec 25 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.6.2-1
- Initial build.
