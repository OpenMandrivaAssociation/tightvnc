Name:    tightvnc
Version: 1.3.10
Release: %mkrel 5

License:   GPLv2+
URL:       http://www.tightvnc.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

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
