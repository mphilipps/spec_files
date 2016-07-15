Summary: run shell commands transparently within perl
Name: perl-shell
Version: 0.73
Release: 1%{?dist}
License: The Perl 5 License
Group: Development/Libraries
URL: http://search.cpan.org/~ferreira/Shell-0.73/
Source: http://search.cpan.org/CPAN/authors/id/F/FE/FERREIRA/Shell-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires: perl(Test::More)
Provides: perl-shell = %{version}-%{release}
BuildRequires: perl(ExtUtils::MakeMaker)

%description
run shell commands transparently within perl


%prep
%setup -q -n Shell-%{version}
find -type f -exec chmod -x {} \;

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor OPTIMIZE="%{optflags}"
%{__make} %{?_smp_mflags}


%install
%{__rm} -rf %{buildroot}
%{__make} pure_install PERL_INSTALL_ROOT=%{buildroot}
find %{buildroot} -type f \( -name .packlist -o \
         -name '*.bs' -size 0 \) -exec rm -f {} ';'
find %{buildroot} -depth -type d -empty -exec rmdir {} ';'
chmod -R u+w %{buildroot}/*

%check
%{__make} test


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_mandir}/man?/*
%{perl_vendorlib}/



%changelog

