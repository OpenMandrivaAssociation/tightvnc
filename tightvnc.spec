%bcond_with     xvnc
%define vnc     vnc

Name:           tightvnc
Version:        1.3.9
Release:        %mkrel 2
Summary:        Remote graphical access
Group:          Networking/Remote access
License:        GPL
URL:            http://www.tightvnc.org/        
Source0:        http://dl.sourceforge.net/vnc-tight/tightvnc-%{version}_unixsrc.tar.bz2
Source1:        http://www.uk.research.att.com/vnc/dist/vnc-latest_doc.tar.bz2
Source2:        %{name}-icons.tar.bz2
Source3:        vncserverinit
Patch1:         vnc-xclients.patch
Patch2:         tightvnc-1.2.6-config-x86_64.patch
Patch3:         vncserver-vncpasswd-1.2.6.patch
Patch4:         vncserver-halfbaked.patch
Patch5:         vncviewer-fix-crash-when-lose-focus.patch
Patch6:         tightvnc-1.2.9-fix-build-when-fds_bits-not-defined.patch
Patch8:         tightvnc-1.2.9-includes.patch
Patch9:         tightvnc-xf4vnc-no-xkb.patch
Patch10:        vnc_unixsrc-CVE-2007-1003.patch
Patch11:        vnc_unixsrc-CVE-2007-1351-1352.patch
Obsoletes:      vnc
Provides:       vnc
Requires(pre):  /usr/bin/perl tcp_wrappers
BuildRequires:  X11-devel zlib-devel tcp_wrappers-devel libjpeg-devel xpm-devel xorg-x11 imake gccmakedep rman
BuildRequires:  libxt-devel libxmu-devel libxaw-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%package server
Summary:        A VNC server
Group:          System/Servers
Requires(post): rpm-helper
Requires(preun): rpm-helper
Obsoletes:      vnc-server vnc-java
Provides:       vnc-server vnc-java
%if %without xvnc
Requires:       x11-server-xvnc
%endif

%description server
The VNC system allows you to access the same desktop from a wide variety
of platforms. This package is a VNC server, allowing  others  to  access
the desktop on your machine.

%package doc
Summary:        Complete documentation for VNC
Group:          Networking/Remote access
Obsoletes:      vnc-doc
Provides:       vnc-doc

%description doc
This package contains HTML  documentation  about  VNC  (Virtual  Network
Computing) programs. Install the vnc-doc package if you  want  extensive
online documentation about VNC.

%prep
%setup -q -n vnc_unixsrc
%setup -q -T -D -a1 -n vnc_unixsrc
%setup -q -T -D -a2 -n vnc_unixsrc
%patch1 -p1 -b .orig
%patch2 -p1 -b .config-x86_64
%patch3 -p1 
%patch4 -p0 -b .halfbaked

%patch5 -p1 -b .fix_crash
%patch6 -p1 -b .fds_bits
%patch8 -p1 -b .includes
%if %without xvnc
# conditional patch ):
%patch9 -p1 -b .no-xkb
%endif
%patch10 -p1 -b .cve-2007-1003
%patch11 -p1 -b .cve-2007-1351-1352

# nuke references to /usr/local
find . -name Imakefile | \
  xargs perl -pi -e "s,(-[IL]/usr/local/(include|lib)),,g"

# remove cvs-files from distribution.
find . -name "*,v" -exec rm -f {} \;
perl -pi -e "s|/usr/local/vnc/classes|%{_datadir}/vnc/classes|" vncserver
perl -pi -e "s|unix/:7100|unix/:-1|" vncserver


%build
%{serverbuild}
xmkmf
make CONFIGDIR=%{_datadir}/X11/config Makefiles
make CONFIGDIR=%{_datadir}/X11/config includes
make CONFIGDIR=%{_datadir}/X11/config depend
make CDEBUGFLAGS="%optflags" CONFIGDIR=%{_datadir}/X11/config World
%if %with xvnc
cd Xvnc
./configure
make EXTRA_LIBRARIES="-lwrap -lnss_nis" CDEBUGFLAGS="%optflags" World \
        EXTRA_DEFINES="-DUSE_LIBWRAP=1"
%endif


%install
rm -rf %{buildroot}

install -D -m 755 vncviewer/vncviewer           %{buildroot}%{_bindir}/vncviewer
install -D -m 755 vncpasswd/vncpasswd           %{buildroot}%{_bindir}/vncpasswd
install -D -m 755 vncconnect/vncconnect         %{buildroot}%{_bindir}/vncconnect
install -D -m 755 vncserver                     %{buildroot}%{_bindir}/vncserver
%if %with xvnc
install -D -m 755 Xvnc/programs/Xserver/Xvnc    %{buildroot}%{_bindir}/Xvnc
%endif

install -D -m 644 vncviewer/vncviewer.man               %{buildroot}%{_mandir}/man1/vncviewer.1
install -D -m 644 vncpasswd/vncpasswd.man               %{buildroot}%{_mandir}/man1/vncpasswd.1
install -D -m 644 vncconnect/vncconnect.man             %{buildroot}%{_mandir}/man1/vncconnect.1
install -D -m 644 vncserver.man                         %{buildroot}%{_mandir}/man1/vncserver.1
install -D -m 644 Xvnc/programs/Xserver/Xvnc.man        %{buildroot}%{_mandir}/man1/Xvnc.1
# 1 extra man page; Xserver.man; This is the  original  Xserver  manpage
# and should only be installed if no X is on the system. I choose not to
# include it.

mkdir -p                                %{buildroot}%{_datadir}/%{vnc}
cp -R classes                           %{buildroot}%{_datadir}/%{vnc}

# Some old docs, better than nothing.
mkdir -p                                %{buildroot}%{_datadir}/%{name}/docs
cp -R vnc_docs/*                        %{buildroot}%{_datadir}/%{name}/docs

# icons
install -D -m 644 %{name}48.png %{buildroot}%{_liconsdir}/%{name}.png
install -D -m 644 %{name}32.png %{buildroot}%{_iconsdir}/%{name}.png
install -D -m 644 %{name}16.png %{buildroot}%{_miconsdir}/%{name}.png

# Menu entry
mkdir -p        %{buildroot}%{_menudir}

cat << EOF >%{buildroot}%{_menudir}/%{name}
?package(%name): \
needs="text" \
section="Internet/Remote Access" \
title="TightVNC" \
icon="tightvnc.png" \
longtitle="Control a pc from anywhere" \
command="vncviewer" \
xdg="true"
EOF

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Tightvnc
Comment=%{summary}
Exec=%{_bindir}/vncviewer
Icon=%{name}
Terminal=true
Type=Application
Categories=X-MandrivaLinux-Internet-RemoteAccess;Network;RemoteAccess; Dialup;
Encoding=UTF-8
EOF

install -d -m0755 %{buildroot}%{_sysconfdir}/sysconfig
cat > %{buildroot}/%{_sysconfdir}/sysconfig/%{vnc}servers << EOF

# The VNCSERVERS variable is a list of display:user pairs.
#
# Uncomment the line below to start a VNC server on  display  :1  as  my
# 'myusername' (adjust this to your own). You will also need  to  set  a
# VNC password;  run 'man vncpasswd' to see how to do that.  Options for
# a vnc server can be appended to the list entry, using : as separator.
#   example:  2:myusername:-geometry:640x480
#
# DO NOT RUN THIS SERVICE if your local area network is untrusted. For a
# secure way of using VNC, see <URL:http://www.tightvnc.org>.

# VNCSERVERS="1:myusername"
EOF

install -m 0755 %SOURCE3 -D %{buildroot}/%{_initrddir}/%{vnc}server

# menu
mkdir -p %{buildroot}%{_menudir}

%clean
rm -rf %{buildroot}

%post
%{update_menus}
%{make_session}

%postun
%{clean_menus}
%{make_session}

%post server
%_post_service vncserver

%preun server
%_preun_service vncserver

%files
%defattr(-,root,root,0755)
%{_bindir}/vncviewer
%defattr(0644,root,root,0755)
%doc ChangeLog README WhatsNew
%{_mandir}/man1/vncviewer.1*
%{_datadir}/%{vnc}/classes/
%{_datadir}/applications/mandriva-%{name}.desktop
%dir %{_datadir}/%{vnc}/
%{_menudir}/%{name}
%{_liconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png

%files doc
%defattr(0644,root,root,0755)
%doc README WhatsNew
%{_datadir}/%{name}/docs/*

%files server
%defattr(-,root,root,0755)
%if %with xvnc
%{_bindir}/Xvnc
%endif
%{_bindir}/vncserver
%{_bindir}/vncpasswd
%{_bindir}/vncconnect
%attr(0755,root,root) %{_initrddir}/%{vnc}server
%{_mandir}/man1/Xvnc.1*
%{_mandir}/man1/vncserver.1*
%{_mandir}/man1/vncconnect.1*
%{_mandir}/man1/vncpasswd.1*
%config(noreplace) %{_sysconfdir}/sysconfig/%{vnc}servers
