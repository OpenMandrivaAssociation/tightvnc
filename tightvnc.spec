%define name	tightvnc
%define version	1.2.9
%define release	%mkrel 16
%define vnc	vnc

# Define to build with upstream Xvnc based on XF86 3.3
%define build_Xvnc 0

Summary:	Remote graphical access	
Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		Networking/Remote access
License:	GPL
URL:		http://www.tightvnc.org/	
Requires(pre):	/usr/bin/perl tcp_wrappers
ExclusiveArch:	%{ix86} alpha sparc ppc s390 s390x x86_64 amd64 ppc64
BuildRequires:	libx11-devel zlib-devel tcp_wrappers-devel libjpeg-devel xpm-devel xorg-x11 imake gccmakedep rman
BuildRequires:	libxt-devel libxmu-devel libxaw-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Source:		http://prdownloads.sourceforge.net/vnc-tight/%{name}-%{version}_unixsrc.tar.bz2
Source1:	http://www.uk.research.att.com/vnc/dist/vnc-latest_doc.tar.bz2
Source2:	%{name}-icons.tar.bz2
Source3:	vncserverinit
Patch1:		vnc-xclients.patch
Patch2:		tightvnc-1.2.6-config-x86_64.patch
Patch3:		vncserver-vncpasswd-1.2.6.patch
Patch4:		vncserver-halfbaked.patch
Patch5:		vncviewer-fix-crash-when-lose-focus.patch
#deush
Patch6:		tightvnc-1.2.9-fix-build-when-fds_bits-not-defined.patch
Patch7:		tightvnc-1.2.9-use-stdlib-malloc.patch
Patch8:		tightvnc-1.2.9-includes.patch
Patch9:		tightvnc-xf4vnc-no-xkb.patch
Patch10:        vnc_unixsrc-CVE-2007-1003.patch
Patch11:        vnc_unixsrc-CVE-2007-1351-1352.patch
Obsoletes:	vnc
Provides:	vnc

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

%package	server
Summary:        A VNC server
Group:          System/Servers
Requires(pre):         /sbin/chkconfig /etc/init.d
Obsoletes:      vnc-server vnc-java
Provides:       vnc-server vnc-java
%if ! %{build_Xvnc}
Requires:	x11-server-xvnc
%endif

%description	server
The VNC system allows you to access the same desktop from a wide variety
of platforms. This package is a VNC server, allowing  others  to  access
the desktop on your machine.

%package	doc
Summary:        Complete documentation for VNC
Group:          Networking/Remote access
Obsoletes:	vnc-doc
Provides:	vnc-doc

%description	doc
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
%patch7 -p1 -b .stdlib_malloc
%patch8 -p1 -b .includes
%if ! %{build_Xvnc}
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
%if %{build_Xvnc}
cd Xvnc
./configure
make EXTRA_LIBRARIES="-lwrap -lnss_nis" CDEBUGFLAGS="%optflags" World \
	EXTRA_DEFINES="-DUSE_LIBWRAP=1"
%endif


%install
rm -rf $RPM_BUILD_ROOT

install -D -m 755 vncviewer/vncviewer           $RPM_BUILD_ROOT%{_bindir}/vncviewer
install -D -m 755 vncpasswd/vncpasswd           $RPM_BUILD_ROOT%{_bindir}/vncpasswd
install -D -m 755 vncconnect/vncconnect         $RPM_BUILD_ROOT%{_bindir}/vncconnect
install -D -m 755 vncserver                     $RPM_BUILD_ROOT%{_bindir}/vncserver
%if %{build_Xvnc}
install -D -m 755 Xvnc/programs/Xserver/Xvnc    $RPM_BUILD_ROOT%{_bindir}/Xvnc
%endif

# Debugging support
if ! [ $DEBUG ]; then
        strip   $RPM_BUILD_ROOT%{_bindir}/vncconnect \
                $RPM_BUILD_ROOT%{_bindir}/vncpasswd  \
                $RPM_BUILD_ROOT%{_bindir}/vncviewer
fi

install -D -m 644 vncviewer/vncviewer.man               $RPM_BUILD_ROOT%{_mandir}/man1/vncviewer.1
install -D -m 644 vncpasswd/vncpasswd.man               $RPM_BUILD_ROOT%{_mandir}/man1/vncpasswd.1
install -D -m 644 vncconnect/vncconnect.man             $RPM_BUILD_ROOT%{_mandir}/man1/vncconnect.1
install -D -m 644 vncserver.man                         $RPM_BUILD_ROOT%{_mandir}/man1/vncserver.1
install -D -m 644 Xvnc/programs/Xserver/Xvnc.man        $RPM_BUILD_ROOT%{_mandir}/man1/Xvnc.1
# 1 extra man page; Xserver.man; This is the  original  Xserver  manpage
# and should only be installed if no X is on the system. I choose not to
# include it.

# bzip2 manpages (should be automatic, dirty);
bzip2 $RPM_BUILD_ROOT/%{_mandir}/man1/*.1

mkdir -p                                $RPM_BUILD_ROOT%{_datadir}/%{vnc}
cp -R classes                           $RPM_BUILD_ROOT%{_datadir}/%{vnc}

# Some old docs, better than nothing.
mkdir -p                                $RPM_BUILD_ROOT%{_datadir}/%{name}/docs
cp -R vnc_docs/*                        $RPM_BUILD_ROOT%{_datadir}/%{name}/docs

# icons
install -D -m 644 %{name}48.png $RPM_BUILD_ROOT%{_liconsdir}/%{name}.png
install -D -m 644 %{name}32.png $RPM_BUILD_ROOT%{_iconsdir}/%{name}.png
install -D -m 644 %{name}16.png $RPM_BUILD_ROOT%{_miconsdir}/%{name}.png

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

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
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

install -d -m0755 %buildroot%_sysconfdir/sysconfig
cat > %buildroot/%_sysconfdir/sysconfig/%{vnc}servers << EOF

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

install -m755 %SOURCE3 -D %buildroot/%{_initrddir}/%{vnc}server

# menu
mkdir -p $RPM_BUILD_ROOT%_menudir


%post
# menu
%{update_menus}
%{make_session}

%postun
# menu
%{clean_menus}
%{make_session}

%post server
if [ "$1" = 1 ]; then
        /sbin/chkconfig --add vncserver
fi

%preun server
if [ "$1" = 0 ]; then
        /sbin/service vncserver stop >/dev/null 2>&1
        /sbin/chkconfig --del vncserver
fi

%postun server
if [ "$1" -ge "1" ]; then
        /sbin/service vncserver condrestart >/dev/null 2>&1
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,755)
%{_bindir}/vncviewer

%defattr(644,root,root,755)
%{_mandir}/man1/vncviewer.1*
%{_datadir}/%{vnc}/classes/
%{_datadir}/applications/mandriva-%{name}.desktop
%dir %{_datadir}/%{vnc}/
%doc ChangeLog README WhatsNew

%{_menudir}/%{name}

%{_liconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png

%files doc
%defattr(644,root,root,755)
%doc README WhatsNew
%{_datadir}/%{name}/docs/*

%files server
%defattr(-,root,root,755)
%attr(0755,root,root) %config(noreplace) %_initrddir/%{vnc}server
%config(noreplace) %_sysconfdir/sysconfig/%{vnc}servers
%if %{build_Xvnc}
%{_bindir}/Xvnc
%endif
%{_bindir}/vncserver
%{_bindir}/vncpasswd
%{_bindir}/vncconnect

#%_datadir/vnc
%{_mandir}/man1/Xvnc.1*
%{_mandir}/man1/vncserver.1*
%{_mandir}/man1/vncconnect.1*
%{_mandir}/man1/vncpasswd.1*

