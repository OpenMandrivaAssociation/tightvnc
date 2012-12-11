Name:		tightvnc
Version:	1.3.10
Release:	6
License:	GPLv2+
URL:		http://www.tightvnc.org

Source0: http://sf.net/projects/vnc-tight/files/TightVNC-unix/%{version}/tightvnc-%{version}_unixsrc.tar.bz2
Source1: http://sf.net/projects/vnc-tight/files/TightVNC-javaviewer/%{version}/tightvnc-%{version}_javasrc.tar.gz
Source2: %{name}-icons.tar.bz2
Source3: vncviewer.desktop

Patch0: 0001-CVE-2007-1003.patch
Patch1: 0002-CVE-2007-1351-1352.patch
Patch2: 0003-Fix-compilation-with-Wformat-Werror-format-security.patch
Patch3: 0004-Fix-font-path.patch
Patch4: 0005-Install-binaries-with-standard-permissions.patch
Patch5: 0006-Fix-java-class-path.patch
Patch6: 0007-Set-source-to-1.3.patch

BuildRequires: gccmakedep
BuildRequires: imake
BuildRequires: java-devel
BuildRequires: libxaw-devel
BuildRequires: libjpeg-devel
BuildRequires: libxmu-devel
BuildRequires: libxp-devel
BuildRequires: libxt-devel
BuildRequires: zlib-devel

# Old tightvnc patch had a "doc" subpackage, but the site that distributed it
# doesn't exist anymore. If we ever add it back, we should do this in a
# different .src.rpm, since the doc files don't belong to the tightvnc project.
Obsoletes: %{name}-doc

#------------------------------------------------------------------------------

# package tightvnc

Summary: Viewer for the VNC remote display system
Group:   Networking/Remote access

Provides:  vncviewer
Conflicts: tigervnc

%description
VNC allows you to access to a remote graphical display through the network.

The enhanced version of VNC, called TightVNC (grown from the  VNC  Tight
Encoder  project), is  optimized  to  work  over  slow   network
connections such as low-speed modem links. While  original  VNC  may  be
very slow when your connection is not fast enough, with TightVNC you can
work  remotely  almost  in  real  time  in  most  environments.  Besides
bandwidth optimizations, TightVNC also includes many other improvements,
optimizations and  bugfixes  over  VNC.  Note  that  TightVNC  is  free,
cross-platform and compatible with the standard VNC.

%files
%defattr(-,root,root)
%{_bindir}/vncviewer
%{_mandir}/man1/vncviewer*
%{_datadir}/applications/vncviewer.desktop
%{_liconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png

#------------------------------------------------------------------------------

%package server

Summary: Server for the VNC remote display system
Group:   Networking/Remote access

Provides:  vnc-server
Conflicts: tigervnc-server

Requires: x11-font-alias
Requires: vnc-server-common

%description server
The VNC system allows you to access the same desktop from a wide variety
of platforms. This package is a VNC server, allowing  others  to  access
the desktop on your machine.

%files server
%defattr(-,root,root)
%{_bindir}/Xvnc
%{_bindir}/vncconnect
%{_bindir}/vncpasswd
%{_bindir}/vncserver
%{_mandir}/man1/Xvnc*
%{_mandir}/man1/vncconnect*
%{_mandir}/man1/vncpasswd*
%{_mandir}/man1/vncserver*

#------------------------------------------------------------------------------

%package java

Summary: Java viewer for the VNC remote display system
Group:   Networking/Remote access

Provides:  vnc-java
Conflicts: tigervnc-java

%description java
This distribution is based on the standard VNC source and includes new
TightVNC-specific features and fixes, such as additional low-bandwidth
optimizations, major GUI improvements, and more.

There are three basic ways to use TightVNC Java viewer:
  1. Running applet as part of TightVNC server installation.
  2. Running applet hosted on a standalone Web server.
  3. Running the viewer as a standalone application.

%files java
%defattr(-,root,root)
%{_javadir}/*.jar
%{_datadir}/%{name}

#------------------------------------------------------------------------------

%prep
%setup -q -n vnc_unixsrc
%setup -q -D -a1 -n vnc_unixsrc
%setup -q -D -a2 -n vnc_unixsrc
%apply_patches

%build
%setup_compile_flags

# client
xmkmf -a
%make CDEBUGFLAGS="$CFLAGS" EXTRA_LDOPTIONS="$LDFLAGS" World

# server
cd Xvnc
%configure
# No %make here: didn't work for me.
# Also, I couldn't find a way to set CFLAGS somewhere without getting build
# errors when building libfont.a.
make EXTRA_LDOPTIONS="$LDFLAGS"
cd ..

# java
cd vnc_javasrc
make all
cd ..

%install
rm -rf %{buildroot}

# client and server
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_mandir}/man1
./vncinstall %{buildroot}%{_bindir} %{buildroot}%{_mandir}

install -d -m 755 %{buildroot}/%{_datadir}/applications
desktop-file-install \
    --dir %{buildroot}%{_datadir}/applications \
    %{_sourcedir}/vncviewer.desktop

install -D -m 644 %{name}48.png %{buildroot}%{_liconsdir}/%{name}.png
install -D -m 644 %{name}32.png %{buildroot}%{_iconsdir}/%{name}.png
install -D -m 644 %{name}16.png %{buildroot}%{_miconsdir}/%{name}.png


# java
install -d -m 755 %{buildroot}%{_javadir}
install -d -m 755 %{buildroot}%{_datadir}/%{name}/classes
cd vnc_javasrc
make install INSTALL_DIR=%{buildroot}%{_datadir}/%{name}/classes \
	     ARCHIVE=vncviewer-%{version}.jar
cd ..
pushd %{buildroot}%{_datadir}/%{name}/classes
mv vncviewer-%{version}.jar %{buildroot}%{_javadir}
ln -s %{_javadir}/vncviewer-%{version}.jar VncViewer.jar
popd
pushd %{buildroot}%{_javadir}
ln -s vncviewer-%{version}.jar vncviewer.jar
ln -s vncviewer-%{version}.jar VncViewer.jar
popd

%clean
rm -rf %{buildroot}


%changelog
* Thu Oct 20 2011 Matthew Dawkins <mattydaw@mandriva.org> 1.3.10-6
+ Revision: 705460
- rebuild

  + Paulo Ricardo Zanoni <pzanoni@mandriva.com>
    - Remove deprecated Encoding key from desktop file

* Wed Dec 29 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.3.10-5mdv2011.0
+ Revision: 626024
- Add patch to change java source path
  Compilation is failing with current values
- Fix -java file paths (so you don't get empty dirs after removing the package)
- Conflict with tigervnc-java
- Try to ressurrect this package
- Change the placement of the sections inside the spec to make it look like the
  other vnc packages.
- Change the descriptions and summaries to make it look like the other vnc
  packages
- Other small changes part of the "vnc spec file standardization"
- Fix URL links
- Ressurrect tightvnc-server. Do not attempt to use a Xvnc based on a newer
  Xorg: use the one provided by tightvnc. If you need Xvnc based on a newer
  Xorg, use tigervnc-server or other package. People installing tightvnc-server
  should expect the Xvnc package provided the tightvnc, not some other.
- Remove "doc" package since its source is not part of the official tightvnc
  source and it can't be found in the original location mentioned inside the
  spec file. If we ever add it back, we should add it in a different package and
  then remove our "Obsoletes" tag.
- Move old undocumented patches to old-patches
- Add patches that are essential to make server and clients work
- Require vnc-server-common instead of providing our own initscripts and
  sysconfig file
- Move the desktop file to a real file (instead of writing it inside the spec).
  Also make it look similar to other vnc's desktop files.
- Use "vncinstall" instead of manually installing the files

* Wed Dec 01 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.3.10-4mdv2011.0
+ Revision: 604501
- Remove useless BR
- Remove useless white spaces

* Sun Jan 10 2010 Oden Eriksson <oeriksson@mandriva.com> 1.3.10-3mdv2010.1
+ Revision: 488805
- rebuilt against libjpeg v8

* Sat Aug 15 2009 Oden Eriksson <oeriksson@mandriva.com> 1.3.10-2mdv2010.0
+ Revision: 416533
- rebuilt against libjpeg v7

* Sun May 03 2009 Funda Wang <fwang@mandriva.org> 1.3.10-1mdv2010.0
+ Revision: 370989
- New version 1.3.10

* Sat Mar 28 2009 Funda Wang <fwang@mandriva.org> 1.3.9-19mdv2009.1
+ Revision: 361912
- BR libxp

* Tue Feb 03 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.9-18mdv2009.1
+ Revision: 337183
- keep bash completion in its own package

* Thu Jan 29 2009 Ander Conselvan de Oliveira <ander@mandriva.com> 1.3.9-17mdv2009.1
+ Revision: 335249
- Do not pass -co (colorPath) option to Xvnc. It was removed on X.org 1.6.
- Rediff patches to apply with fuzz=0
- Fix for -Werror=format-security

* Fri Sep 05 2008 Adam Williamson <awilliamson@mandriva.org> 1.3.9-16mdv2009.0
+ Revision: 280997
- obsolete nxviewer (a fork of vncviewer for nx which was dropped with nx
  3.2.0)

* Tue Aug 05 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.3.9-15mdv2009.0
+ Revision: 263757
- Show back on kde menu

* Mon Jul 07 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.3.9-14mdv2009.0
+ Revision: 232625
- Do not show on KDE menu ( KDE menu cleaning task )

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 1.3.9-13mdv2009.0
+ Revision: 225716
- rebuild
- kill re-definition of %%buildroot on Pixel's request

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

  + Anssi Hannula <anssi@mandriva.org>
    - fix Xvnc build (remove Xvnc buildfix patch5)
    - server conflicts with x11-server-xvnc when building with --with xvnc

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 1.3.9-12mdv2008.1
+ Revision: 121030
- buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Sat Nov 24 2007 David Walluck <walluck@mandriva.org> 1.3.9-11mdv2008.1
+ Revision: 111733
- copy/link java files to correct location

* Fri Nov 23 2007 David Walluck <walluck@mandriva.org> 1.3.9-10mdv2008.1
+ Revision: 111689
- enable and fix colorPath

* Sun Nov 18 2007 David Walluck <walluck@mandriva.org> 1.3.9-9mdv2008.1
+ Revision: 109788
- fix font path

* Mon Oct 15 2007 David Walluck <walluck@mandriva.org> 1.3.9-8mdv2008.1
+ Revision: 98727
- fix font path

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 1.3.9-7mdv2008.0
+ Revision: 87208
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

  + Thierry Vignaud <tv@mandriva.org>
    - kill desktop-file-validate's 'warning: key "Encoding" in group "Desktop Entry" is deprecated'

* Sat Aug 18 2007 David Walluck <walluck@mandriva.org> 1.3.9-6mdv2008.0
+ Revision: 65438
- fix menu comment
- add some releases to the provides/obsoletes

* Thu Jul 05 2007 David Walluck <walluck@mandriva.org> 1.3.9-5mdv2008.0
+ Revision: 48408
- BuildRequires: jpackage-util
- add versioned obsoletes/provides
- build java classes
- mark file in %%{_sysconfdir} as %%config(noreplace)
- fix executable perms on files in doc package

* Wed Jul 04 2007 Andreas Hasenack <andreas@mandriva.com> 1.3.9-4mdv2008.0
+ Revision: 48262
- use new serverbuild macro (-fstack-protector-all)

* Wed Jun 27 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.9-3mdv2008.0
+ Revision: 44904
- handle doc manually, as %%doc macro sux
- don't ship java binaries
- clean up installation and file list
- drop old debian menu
- bash completion
- drop mandriva-specific category in menu

* Tue May 08 2007 David Walluck <walluck@mandriva.org> 1.3.9-2mdv2008.0
+ Revision: 25024
- use cp -a instead of cp -R
- one BuildRequires per line
- remove bogus Requires(pre)
- remove extra mkdir for menudir
- LSB initscript
- renumber patches
-remove ExclusiveArch
- no need to force bzip2 manpages
- use with option for xvnc
- 1.3.9

* Sat May 05 2007 Lenny Cartier <lenny@mandriva.org> 1.2.9-16mdv2008.0
+ Revision: 22620
- Apply CVE patches 2007-1003 and 2007-1351-1352 (Bug #29820)


* Wed Oct 18 2006 Christiaan Welvaart <cjw@daneel.dyndns.org>
+ 2006-10-18 19:42:07 (71005)
- allow arbitrary vncserer options in sysconfig file
- always pass -kb to xf4vnc Xvnc (fixes bug #21031)

* Fri Oct 13 2006 Christiaan Welvaart <cjw@daneel.dyndns.org>
+ 2006-10-13 11:58:09 (64558)
- rebuild to get x86-64 packages

* Thu Oct 12 2006 Christiaan Welvaart <cjw@daneel.dyndns.org>
+ 2006-10-12 19:26:34 (64469)
- fix build on x86-64

* Thu Oct 12 2006 Christiaan Welvaart <cjw@daneel.dyndns.org>
+ 2006-10-12 09:56:19 (63796)
- use x11-server-xvnc
- add BuildRequires: libxt-devel libxmu-devel libxaw-devel

* Thu Oct 12 2006 Christiaan Welvaart <cjw@daneel.dyndns.org>
+ 2006-10-12 09:43:57 (63790)
Import tightvnc

* Wed Sep 06 2006 Lenny Cartier <lenny@mandriva.com> 1.2.9-13mdv2007.0
- enable build of Xvnc

* Sat Aug 26 2006 Emmanuel Andry <eandry@mandriva.org> 1.2.9-12mdv2007.0
- fix x11 path (bug #23248)
- xdg menu

* Tue Jun 20 2006 Lenny Cartier <lenny@mandriva.com> 1.2.9-11mdv2007.0
- try to fix Bug #15988 with patch from Tim Edwards
- fix group

* Sun Jun 11 2006 Jerome Soyer <saispo@mandriva.org> 1.2.9-1mdv2007.0
- Fix changelog

* Sun Jun 11 2006 Jerome Soyer <saispo@mandriva.org> 1.2.9-9mdk
- Shlomi Fish <shlomif@iglu.org.il> 1.2.9-9mdk
- Ported to Mandriva 2007 and its xorg-x11 dependencies.

* Tue Jan 24 2006 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.2.9-8mdk
- build on ppc64
- more includes & 64-bit fixes
- use Xvnc server from X.org, i.e. drop ancient one based on XFree86 3.3

* Sun Jan 01 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 1.2.9-7mdk
- Rebuild

* Mon May 30 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.2.9-6mdk
- includes & 64-bit fixes

* Wed Dec 22 2004 Per Ãyvind Karlsen <peroyvind@linux-mandrake.com> 1.2.9-5mdk
- fix buildrequires
- cosmetics

* Fri Sep 03 2004 Daouda LO <daouda@mandrakesoft.com> 1.2.9-4mdk
- The requirement for the fd_set structure to have a member fds_bits 
  has been removed as per The Open Group Base Resolution
- do not redefine malloc (use stdlib one) -> keep synced with Xorg.
- fix menu entry (fcrozat)

* Sat Apr 10 2004 Michael Scherer <misc@mandrake.org> 1.2.9-3mdk 
- [DIRM]
- A better description

* Tue Mar 16 2004 Laurent MONTEL <lmontel@mandrakesoft.com> 1.2.9-2mdk
- Add patch5: fix crash into kwin and co, patch from Lubos Lunak <l.lunak@suse.cz>

* Sat Dec 13 2003 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.2.9-1mdk
- 1.2.9

