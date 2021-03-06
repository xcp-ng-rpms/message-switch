Name:           message-switch
Version:        1.23.0
Release:        1.2%{?dist}
Summary:        A store and forward message switch
License:        FreeBSD
URL:            https://github.com/xapi-project/message-switch

Source0: https://code.citrite.net/rest/archive/latest/projects/XSU/repos/message-switch/archive?at=v1.23.0&format=tar.gz&prefix=message-switch-1.23.0#/message-switch-1.23.0.tar.gz
Source1: SOURCES/message-switch/message-switch.service
Source2: SOURCES/message-switch/message-switch-conf
Source3: SOURCES/message-switch/message-switch-bugtool1.xml
Source4: SOURCES/message-switch/message-switch-bugtool2.xml


Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XSU/repos/message-switch/archive?at=v1.23.0&format=tar.gz&prefix=message-switch-1.23.0#/message-switch-1.23.0.tar.gz) = 6b44a09aad99efcb3cbf43688f6f8f5aa62761d3

BuildRequires:  xs-opam-repo
BuildRequires:  openssl-devel
BuildRequires:  systemd
%{?systemd_requires}

%global _use_internal_dependency_generator 0
%global __requires_exclude *caml*

%description
A store and forward message switch for OCaml.

%global ocaml_dir %{_opamroot}/ocaml-system
%global ocaml_libdir %{ocaml_dir}/lib
%global ocaml_docdir %{ocaml_dir}/doc

%prep
%autosetup -p1
cp %{SOURCE2} message-switch-conf
cp %{SOURCE3} message-switch.xml
cp %{SOURCE4} stuff.xml

%build
./configure --destdir %{buildroot} --sbindir %{_sbindir}
make

%check
make test

%install
mkdir -p %{buildroot}/%{_sbindir}
mkdir -p %{buildroot}%{ocaml_libdir}
mkdir -p %{buildroot}%{ocaml_docdir}
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}/%{_sysconfdir}/init.d
%{__install} -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/message-switch.service
install -m 0644 message-switch-conf %{buildroot}/etc/message-switch.conf

mkdir -p %{buildroot}/etc/xensource/bugtool/message-switch
install -m 0644 message-switch.xml %{buildroot}/etc/xensource/bugtool/message-switch.xml
install -m 0644 stuff.xml %{buildroot}/etc/xensource/bugtool/message-switch/stuff.xml

%files
%{_unitdir}/message-switch.service
%{_sbindir}/message-switch
%{_sbindir}/message-cli
%config(noreplace) /etc/message-switch.conf
/etc/xensource/bugtool/message-switch/stuff.xml
/etc/xensource/bugtool/message-switch.xml

%post
%systemd_post message-switch.service
if [ $1 -gt 1 ] ; then
  # upgrade from SysV, see http://0pointer.de/public/systemd-man/daemon.html
  # except %triggerun doesn't work since previous package had no systemd,
  # and don't transition in 2 steps
  if /sbin/chkconfig --level 5 message-switch ; then
    /bin/systemctl --no-reload enable message-switch.service >/dev/null 2>&1 || :
    /sbin/chkconfig --del message-switch >/dev/null 2>&1 || :
  else
    # remove broken symlinks that a previous version of the package may have forgotten to remove
    find /etc/rc.d -name "*message-switch" -delete >/dev/null 2>&1 || :
  fi
fi

%preun
%systemd_preun message-switch.service

%postun
%systemd_postun

# this would be done by %postun of old package, except old package wasn't
# using systemd, without this a systemctl restart message-switch would fail
# after an upgrade
%posttrans
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%package        devel
Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XSU/repos/message-switch/archive?at=v1.23.0&format=tar.gz&prefix=message-switch-1.23.0#/message-switch-1.23.0.tar.gz) = 6b44a09aad99efcb3cbf43688f6f8f5aa62761d3
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}
Requires:       xs-opam-repo

%description    devel
The %{name}-devel package contains libraries and signature files for
developing applications that use %{name}.

%files devel
%doc LICENSE README.md CHANGES
%defattr(-,root,root,-)
%{ocaml_docdir}/message-switch-core/*
%{ocaml_docdir}/message-switch-unix/*
%{ocaml_docdir}/message-switch-async/*
%{ocaml_docdir}/message-switch-lwt/*
%{ocaml_libdir}/message-switch-core/*
%{ocaml_libdir}/message-switch-unix/*
%{ocaml_libdir}/message-switch-async/*
%{ocaml_libdir}/message-switch-lwt/*
%exclude %{ocaml_libdir}/message-switch-core/*.cmt
%exclude %{ocaml_libdir}/message-switch-core/*.cmti
%exclude %{ocaml_libdir}/message-switch-unix/*.cmt
%exclude %{ocaml_libdir}/message-switch-unix/*.cmti
%exclude %{ocaml_libdir}/message-switch-async/*.cmt
%exclude %{ocaml_libdir}/message-switch-async/*.cmti
%exclude %{ocaml_libdir}/message-switch-lwt/*.cmt
%exclude %{ocaml_libdir}/message-switch-lwt/*.cmti


%changelog
* Tue May 18 2021 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.23.0-1.2
- Rebuild for xs-opam-src 6.35.6 from XS82E20

* Thu Nov 05 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.23.0-1.1
- Rebuild for xs-opam-src 6.35.1 from XS82E002

* Fri Mar 27 2020 Christian Lindig <christian.lindig@citrix.com> - 1.23.0-1
- CP-33380: update opam for dune 2 test compatibility
- travis: refresh configuration

* Fri Aug 23 2019 Edwin Török <edvin.torok@citrix.com> - 1.22.0-2
- bump packages after xs-opam update

* Mon Jul 29 2019 Christian Lindig <christian.lindig@citrix.com> - 1.22.0-1
- Upgrade from jbuilder to dune in opam rules
- Update message-switch dependencies according to dune

* Tue Jul 23 2019 Rob Hoes <rob.hoes@citrix.com> - 1.21.0-1
- CA-323813: do not loop infinitely when there is a communication error with message switch

* Tue Jun 25 2019 Christian Lindig <christian.lindig@citrix.com> - 1.20.0-1
- CA-322044: Fix file descriptor leak on reconnect

* Mon Feb 04 2019 Christian Lindig <christian.lindig@citrix.com> - 1.19.0-2
- Remove stale /etc/rc.d/*/*message-switch symlinks

* Wed Jan 23 2019 Christian Lindig <christian.lindig@citrix.com> - 1.19.0-1
- Prepare for Dune 1.6
- Use Ocaml 4.07 in Travis

* Tue Nov 27 2018 Christian Lindig <christian.lindig@citrix.com> - 1.18.0-1
- Port to dune.
- Removed switch -p as it is causing more packags to be installed than expected.

* Thu Nov 22 2018 Christian Lindig <christian.lindig@citrix.com> - 1.17.0-1
- Add lwt_log to jbuild

* Wed Oct 31 2018 Christian Lindig <christian.lindig@citrix.com> - 1.16.0-1
- Update opam files for Opam 2

* Mon Sep 24 2018 Christian Lindig <christian.lindig@citrix.com> - 1.15.0-1
- message-switch-core.opam: we use rpclib not the old rpc
- Update Travis to use our xs-opam remote

* Tue Sep 18 2018 Christian Lindig <christian.lindig@citrix.com> - 1.14.0-1
- Move to Dune, address compiler warnings
- Replace Re.Str with Astring.String for thread safety

* Fri Aug 31 2018 Christian Lindig <christian.lindig@citrix.com> - 1.13.0-1
- Simplify PPX processing in jbuild files

* Thu May 24 2018 Christian Lindig <christian.lindig@citrix.com> - 1.12.0-1
- CA-289145: close socket if error occurs when using lwt connect
- switch/switch_main: make safe-string compliant
- unix/protocol_unix{,scheduler}: make safe-string compliant
- Fix coverage call

* Wed Apr 04 2018 Marcello Seri <marcello.seri@citrix.com> - 1.11.0-6
- Update SPEC file to get rid of rpmbuild warnings

* Fri Jan 26 2018 Christian Lindig <christian.lindig@citrix.com> - 1.11.0-1
- Update dependencies for new cohttp
- Use Core, Async instead of their deprecated Std submodules
- switch/time: switch to signature expected by shared-block-ring
- switch/clock: use Mtime_clock to satisfy CLOCK signature of shared-block-ring
- Update to new Mirage 3 Block module
- Switch to nanoseconds used by new shared-block-ring interface
- Updates to be compliant with upstream cohttp updates to 0.10.0
- message-switch-lwt: update dependencies
- message-switch, message-switch-async: update dependencies
- jbuild files: update dependencies
- message-switch: update dependencies
- Update .coverage.sh

* Fri Jan 19 2018 Christian Lindig <christian.lindig@citrix.com> - 1.10.0-1
- Minor corrections as per markdown lint.
- CP-26471: Ported build from oasis to jbuilder.
- Added code for coverage.
- Wrapped the modules in their respective libraries.

* Thu Jan 11 2018 Konstantina Chremmou <konstantina.chremmmou@citrix.com> - 1.9.0-2
- Ported build from oasis to jbuilder

* Mon Dec 18 2017 Christian Lindig <christian.lindig@citrix.com> - 1.9.0-1
- CA-261580: Rough port to systemd
- opam: add systemd dependency
- Drop daemonize

* Fri Sep 22 2017 Rob Hoes <rob.hoes@citrix.com> - 1.8.0-1
- Use newer mtime
- .travis.yml: update OCaml version to 4.04

* Mon Jul 24 2017 Rob Hoes <rob.hoes@citrix.com> - 1.7.0-1
- CA-256884: do not crash on client ECONNRESET

* Wed Jul 12 2017 Rob Hoes <rob.hoes@citrix.com> - 1.6.0-1
- CA-248467: message-cli tail --follow causes VM reboot too slow

* Fri Jun 16 2017 Jon Ludlam <jonathan.ludlam@citrix.com> - 1.5.0-1
- opam: sync with xs-opam

* Fri May 12 2017 Rob Hoes <rob.hoes@citrix.com> - 1.4.0-1
- use xs-opam as remote for travis
- add sudo requirement to unlock the build
- Allow failable build with upstream opam repo
- Travis fixes

* Wed Mar 22 2017 Rob Hoes <rob.hoes@citrix.com> - 1.3.0-1
- opam: Fix errors/warnings from `opam lint` command

* Mon Mar 13 2017 Marcello Seri <marcello.seri@citrix.com> - 1.2.1-2
- Update OCaml dependencies and build/install script after xs-opam-repo split

* Thu Mar 02 2017 Gabor Igloi <gabor.igloi@citrix.com> - 1.2.1-1
- Port to xs-opam-repo providing newer, ppx-based libraries

* Wed Mar 01 2017 Rob Hoes <rob.hoes@citrix.com> - 1.1.0-1
- Lwt_unix.run -> Lwt_main.run - Lwt 2.7.0 compatibility
- Minimal change to not conflict with Result.result
- Rename Switch to prevent conlict with newer OCaml
- Remove use of camlp4 lwt syntax extension
- _oasis: remove unneded rpclib.syntax dependencies

* Tue Jan 10 2017 Rob Hoes <rob.hoes@citrix.com> - 1.0.1-1
- git: Add metadata to the result of `git archive`

* Mon May 16 2016 Si Beaumont <simon.beaumont@citrix.com> - 1.0.0-2
- Re-run chkconfig on upgrade

* Wed Apr 13 2016 Si Beaumont <simon.beaumont@citrix.com> - 1.0.0-1
- Update to 1.0.0

* Thu Jul 16 2015 David Scott <dave.scott@citrix.com> - 0.12.0-1
- Add bugtool collection
- Several bugfixes

* Mon Jun 15 2015 David Scott <dave.scott@citrix.com> - 0.11.0-3
- Add blocking fix.

* Fri Jun 12 2015 David Scott <dave.scott@citrix.com> - 0.11.0-2
- Add tail-recursion fix

* Thu Apr 23 2015 David Scott <dave.scott@citrix.com> - 0.11.0-1
- Update to 0.11.0

* Sun Apr 19 2015 David Scott <dave.scott@citrix.com> - 0.10.5.1-2
- Fix for bug exposed by cohttp upgrade

* Thu Apr  2 2015 David Scott <dave.scott@citrix.com> - 0.10.5.1-1
- Update to 0.10.5.1

* Tue Oct 14 2014 David Scott <dave.scott@citrix.com> - 0.10.4-1
- Update to 0.10.4, enable core/async

* Thu Jun 19 2014 David Scott <dave.scott@citrix.com> - 0.10.3-1
- Update to 0.10.3

* Fri Jun 6 2014 Jon Ludlam <jonathan.ludlam@citrix.com> - 0.10.2-1
- Update to 0.10.2

* Fri Oct 18 2013 David Scott <dave.scott@eu.citrix.com> - 0.10.1-1
- Update to 0.10.1 which is more tolerant of startup orderings

* Thu May 30 2013 David Scott <dave.scott@eu.citrix.com>
- Initial package

