%bcond_with     xvnc
%define vnc     vnc
%define gcj_support 1

Name:           tightvnc
Version:        1.3.9
Release:        %mkrel 12
Summary:        Remote graphical access
Group:          Networking/Remote access
License:        GPL
URL:            http://www.tightvnc.org/        
Source0:        http://dl.sourceforge.net/vnc-tight/tightvnc-%{version}_unixsrc.tar.bz2
Source1:        http://www.uk.research.att.com/vnc/dist/vnc-latest_doc.tar.bz2
Source2:        %{name}-icons.tar.bz2
Source3:        vncserverinit
Source4:        %{name}.bash-completion
Source5:        http://downloads.sourceforge.net/vnc-tight/tightvnc-%{version}_javasrc.tar.gz
Patch0:         vnc-xclients.patch
Patch1:         tightvnc-1.2.6-config-x86_64.patch
Patch2:         vncserver-vncpasswd-1.2.6.patch
Patch3:         vncserver-halfbaked.patch
Patch4:         vncviewer-fix-crash-when-lose-focus.patch
Patch5:         tightvnc-1.2.9-fix-build-when-fds_bits-not-defined.patch
Patch6:         tightvnc-1.2.9-includes.patch
Patch7:         tightvnc-xf4vnc-no-xkb.patch
Patch8:         vnc_unixsrc-CVE-2007-1003.patch
Patch9:         vnc_unixsrc-CVE-2007-1351-1352.patch
Obsoletes:      vnc < %{version}-%{release}
Provides:       vnc = %{version}-%{release}
BuildRequires:  gccmakedep
BuildRequires:  imake
BuildRequires:  libjpeg-devel
BuildRequires:  libxpm-devel
BuildRequires:  libxt-devel
BuildRequires:  libxmu-devel
BuildRequires:  libxaw-devel
BuildRequires:  libz-devel
BuildRequires:  rman
BuildRequires:  tcp_wrappers-devel
BuildRequires:  X11-devel
BuildRequires:  xorg-x11

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
Obsoletes:      vnc-server < %{version}-%{release}
Provides:       vnc-server = %{version}-%{release}
%if %without xvnc
Requires:       x11-server-xvnc
%endif

%description server
The VNC system allows you to access the same desktop from a wide variety
of platforms. This package is a VNC server, allowing  others  to  access
the desktop on your machine.

%package java
Summary:        A VNC server
Group:          Development/Java
Obsoletes:      vnc-java < %{version}-%{release}
Provides:       vnc-java = %{version}-%{release}
BuildRequires:  java-rpmbuild
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
BuildRequires:  java-devel
%endif

%description java
The VNC system allows you to access the same desktop from a wide variety
of platforms. This package is a VNC server, allowing  others  to  access
the desktop on your machine.

%package doc
Summary:        Complete documentation for VNC
Group:          Networking/Remote access
Obsoletes:      vnc-doc < %{version}-%{release}
Provides:       vnc-doc = %{version}-%{release}

%description doc
This package contains HTML  documentation  about  VNC  (Virtual  Network
Computing) programs. Install the vnc-doc package if you  want  extensive
online documentation about VNC.

%prep
%setup -q -n vnc_unixsrc
%setup -q -T -D -a1 -n vnc_unixsrc
%setup -q -T -D -a2 -n vnc_unixsrc
%setup -q -T -D -a5 -n vnc_unixsrc
%{__perl} -pi -e 's/ \-O//' vnc_javasrc/Makefile
%patch0 -p1
%patch1 -p1
%patch2 -p1 
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%if %without xvnc
%patch7 -p1
%endif
%patch8 -p1
%patch9 -p1

# nuke references to /usr/local
find . -name Imakefile | \
  xargs perl -pi -e "s,(-[IL]/usr/local/(include|lib)),,g"

# remove cvs-files from distribution.
find . -name "*,v" -exec rm -f {} \;
perl -pi -e "s|/usr/local/vnc/classes|%{_datadir}/vnc/classes|" vncserver
perl -pi -e 's|^\$fontPath =.*|\$fontPath = "catalogue:%{_sysconfdir}/X11/fontpath.d/";|' vncserver
perl -pi -e 's|^# \$colorPath =.*|\$colorPath = "/usr/share/X11/rgb.txt";|' vncserver

%build
%{serverbuild}
xmkmf
make CONFIGDIR=%{_datadir}/X11/config Makefiles
make CONFIGDIR=%{_datadir}/X11/config includes
make CONFIGDIR=%{_datadir}/X11/config depend
make CDEBUGFLAGS="$RPM_OPT_FLAGS" CONFIGDIR=%{_datadir}/X11/config World
%if %with xvnc
cd Xvnc
./configure
make EXTRA_LIBRARIES="-lwrap -lnss_nis" CDEBUGFLAGS="$RPM_OPT_FLAGS" World \
        EXTRA_DEFINES="-DUSE_LIBWRAP=1"
%endif

cd vnc_javasrc
%{__make} ARCHIVE=vncviewer-%{version}.jar CP=%{__cp} JC=%{javac} JCFLAGS="-g" JAR=%{jar} INSTALL_DIR= clean all

%install
rm -rf %{buildroot}

install -d -m 755 %{buildroot}%{_bindir}
install -m 755 vncviewer/vncviewer %{buildroot}%{_bindir}/vncviewer
install -m 755 vncpasswd/vncpasswd %{buildroot}%{_bindir}/vncpasswd
install -m 755 vncconnect/vncconnect %{buildroot}%{_bindir}/vncconnect
install -m 755 vncserver %{buildroot}%{_bindir}/vncserver
%if %with xvnc
install -m 755 Xvnc/programs/Xserver/Xvnc %{buildroot}%{_bindir}/Xvnc
%endif

install -d -m 755 %{buildroot}%{_mandir}/man1
install -m 644 vncviewer/vncviewer.man %{buildroot}%{_mandir}/man1/vncviewer.1
install -m 644 vncpasswd/vncpasswd.man %{buildroot}%{_mandir}/man1/vncpasswd.1
install -m 644 vncconnect/vncconnect.man %{buildroot}%{_mandir}/man1/vncconnect.1
install -m 644 vncserver.man %{buildroot}%{_mandir}/man1/vncserver.1
install -m 644 Xvnc/programs/Xserver/Xvnc.man %{buildroot}%{_mandir}/man1/Xvnc.1
# 1 extra man page; Xserver.man; This is the  original Xserver manpage
# and should only be installed if no X is on the system. I choose not to
# include it.

# handle documentation manually
install -d -m 755 %{buildroot}%{_docdir}/%{name}
install -m 644 ChangeLog README WhatsNew %{buildroot}%{_docdir}/%{name}
cp -a vnc_docs/* %{buildroot}%{_docdir}/%{name}

# icons
install -D -m 644 %{name}48.png %{buildroot}%{_liconsdir}/%{name}.png
install -D -m 644 %{name}32.png %{buildroot}%{_iconsdir}/%{name}.png
install -D -m 644 %{name}16.png %{buildroot}%{_miconsdir}/%{name}.png

# Menu entry
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Tightvnc
Comment=Remote graphical access
Exec=%{_bindir}/vncviewer
Icon=tightvnc
Terminal=true
Type=Application
Categories=Network;RemoteAccess;Dialup;
EOF

install -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
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

install -m 0755 %{SOURCE3} -D %{buildroot}/%{_initrddir}/%{vnc}server

# bash completion
install -d -m 755 %{buildroot}%{_sysconfdir}/bash_completion.d
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}

%{__mkdir_p} %{buildroot}%{_javadir}
cd vnc_javasrc
%{__make} ARCHIVE=vncviewer-%{version}.jar CP=%{__cp} JC=%{javac} JCFLAGS="-g" JAR=%{jar} INSTALL_DIR=%{buildroot}%{_javadir} install
(cd %{buildroot}%{_javadir} && %{__ln_s} vncviewer-%{version}.jar VncViewer-%{version}.jar)
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)
%{__rm} %{buildroot}%{_javadir}/*.class

%{__mkdir_p} %{buildroot}%{_datadir}/vnc/classes
%{__cp} -a index.vnc %{buildroot}%{_datadir}/vnc/classes
(cd %{buildroot}%{_datadir}/vnc/classes && %{__ln_s} VncViewer.jar VncViewer.jar)

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

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

%if %{gcj_support}
%post java
%{update_gcjdb}

%postun java
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root)
%dir %{_docdir}/%{name}
%{_docdir}/%{name}/README
%{_docdir}/%{name}/WhatsNew
%{_docdir}/%{name}/ChangeLog
%{_bindir}/vncviewer
%config(noreplace) %{_sysconfdir}/bash_completion.d/%{name}
%{_mandir}/man1/vncviewer.1*
%{_datadir}/applications/mandriva-%{name}.desktop
%{_liconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png

%files doc
%defattr(0644,root,root,0755)
%{_docdir}/%{name}/*
%exclude %{_docdir}/%{name}/README
%exclude %{_docdir}/%{name}/WhatsNew
%exclude %{_docdir}/%{name}/ChangeLog

%files server
%defattr(-,root,root)
%doc vnc_javasrc/{LICENCE.TXT,README,WhatsNew,index.html}
%if %with xvnc
%{_bindir}/Xvnc
%endif
%{_bindir}/vncserver
%{_bindir}/vncpasswd
%{_bindir}/vncconnect
%{_initrddir}/%{vnc}server
%{_mandir}/man1/Xvnc.1*
%{_mandir}/man1/vncserver.1*
%{_mandir}/man1/vncconnect.1*
%{_mandir}/man1/vncpasswd.1*
%config(noreplace) %{_sysconfdir}/sysconfig/%{vnc}servers

%files java
%defattr(0644,root,root,0755)
%{_javadir}/*
%{_datadir}/vnc
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif
