Summary: Milter helper for Amavisd-new
Name: amavisd-milter
Version: 1.6.1
Release: 1
License: Petr Rehor <rx@rx.cz>. All rights reserved.
Group: System Environment/Daemons
URL: http://amavisd-milter.sourceforge.net/

Packager: Jo Rhett <jrhett@netconsonance.com>
Vendor: Amavisd-new

Source: http://sourceforge.net/projects/amavisd-milter/files/amavisd-milter/amavisd-milter-1.6.1/amavisd-milter-1.6.1.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Requires: amavisd-new sendmail-milter

%description
amavisd-milter is a milter (mail filter) for amavisd-new 2.4.3 and above which uses the AM.PDP protocol.
It has been tested to work with mail servers sendmail 8.13+ and postfix 2.9+

%prep
%setup -n %{name}-%{version}

%{__cat} <<'EOF' >amavisd-milter.sysconfig
#         User to run under (must be same as amavisd daemon)
AMAVIS_USER=amavis

#         Set working directory (default /var/amavis).
#WORKING_DIRECTORY=/var/amavis

#         Communication socket between sendmail and amavisd-milter (default
#         /var/amavis/amavisd-milter.sock).  The protocol spoken over this
#         socket is MILTER (Mail FILTER).  It must agree with the
#         INPUT_MAIL_FILTER entry in sendmail.mc
#         The socket should be in "proto:address" format:
#         o   {unix|local}:/path/to/file - A named pipe.
#         o   inet:port@{hostname|ip-address} - An IPV4 socket.
#         o   inet6:port@{hostname|ip-address} - An IPV6 socket.
#SOCKET=/var/amavis/amavisd-milter.sock

#         Use this pid file (default /var/amavis/amavisd-milter.pid).
#         Better to create /var/run/amavis and put it there
#PID_FILE=/var/run/amavis/amavisd-milter.pid

#         Maximum concurrent amavisd connections (default 0 - unlimited
#         number of connections).  It must agree with the $max_servers
#         entry in amavisd.conf.
#MAX_CONNECTIONS=0

#         Maximum wait for connection to amavisd in seconds (default 300 =
#         5 minutes).  It must be less then sending MTA timeout for a
#         response to the final "."  that terminates a message on sending
#         MTA.  sendmail has default value 1 hour, postfix 10 minutes and
#         qmail 20 minutes.  We suggest to use less than 10 minutes.
#MAX_WAIT=300

#         sendmail connection timeout in seconds (default 600 = 10 min-
#         utes).  It must agree with the INPUT_MAIL_FILTER entry in send-
#         mail.mc and must be greater than or equal to the amavisd-new con-
#         nection timeout.  When you use other milters (especially time-
#         consuming), the timeout must be sufficient to process message in
#         all milters.
#MAILDAEMON_TIMEOUT=600

#         amavisd-new connection timeout in seconds (default 600 = 10 min-
#         utes).  This timeout must be sufficient for message processing in
#         amavisd-new.  It's usually a good idea to adjust them to the same
#         value as sendmail connection timeout.
#AMAVISD_TIMEOUT=600
EOF

%{__cat} <<'EOF' >amavisd-milter.init
#!/bin/bash
#
# Init script for amavisd-milter
# Copyright (c) 2005, Petr Rehor <rx@rx.cz>. All rights reserved.
#
# chkconfig: 2345 71 41
# description: amavisd-milter
#
# processname: amavisd-milter
# pidfile: %{_localstatedir}/run/amavis/amavisd-milter.pid

source %{_initrddir}/functions
[ -r %{_sysconfdir}/amavisd.conf ] || exit 1

### Read configuration
SYSCONFIG="%{_sysconfdir}/sysconfig/amavisd-milter"
[ -r "$SYSCONFIG" ] && source "$SYSCONFIG"

# Defaults which must be set
if [ -z $AMAVIS_USER ]; then
    AMAVIS_USER=amavis
fi
if [ -z $WORKING_DIRECTORY ]; then
    WORKING_DIRECTORY=/var/amavis
fi
if [ -z $PID_FILE ]; then
    PID_FILE=/var/amavis/amavisd-milter.pid
fi
if [ -z $SOCKET ]; then
    SOCKET=var/amavis/amavisd-milter.sock
fi
OPTIONS="-s $SOCKET -p $PID_FILE -w $WORKING_DIRECTORY"

if [ ! -z $MAX_CONNECTIONS ]; then
    OPTIONS="$OPTIONS -m $MAX_CONNECTIONS"
fi
if [ ! -z $MAX_WAIT ]; then
    OPTIONS="$OPTIONS -M $MAX_WAIT"
fi
if [ ! -z $MAILDAEMON_TIMEOUT ]; then
    OPTIONS="$OPTIONS -t $MAILDAEMON_TIMEOUT"
fi
if [ ! -z $AMAVISD_TIMEOUT ]; then
    OPTIONS="$OPTIONS -T $AMAVISD_TIMEOUT"
fi

RETVAL=0
prog="amavisd-milter"
desc="Amavisd milter helper"

start() {
	echo -n $"Starting $desc ($prog): "
	daemon --user ${AMAVIS_USER} --pidfile=${PID_FILE} %{_sbindir}/$prog ${OPTIONS}
	RETVAL=$?
	echo
	[ $RETVAL -eq 0 ] && touch %{_localstatedir}/lock/subsys/$prog
	return $RETVAL
}

stop() {
	echo -n $"Shutting down $desc ($prog): "
    killproc -p ${PID_FILE} $prog
	RETVAL=$?
	echo
	[ $RETVAL -eq 0 ] && rm -f %{_localstatedir}/lock/subsys/$prog
	return $RETVAL
}

restart() {
	stop
	start
}

case "$1" in
  start)
	start
	;;
  stop)
	stop
	;;
  restart)
	restart
	;;
  condrestart)
	[ -e %{_localstatedir}/lock/subsys/$prog ] && restart
	RETVAL=$?
	;;
  status)
	status -p ${PID_FILE} $prog
	RETVAL=$?
	;;
  *)
	echo $"Usage: $0 {start|stop|restart|condrestart|status}"
	RETVAL=1
esac

exit $RETVAL
EOF

%build
%configure
make %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%makeinstall
%{__install} -D -m0755 amavisd-milter.init %{buildroot}%{_initrddir}/amavisd-milter
%{__install} -D -m0644 amavisd-milter.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/amavisd-milter

%clean
%{__rm} -rf %{buildroot}

%pre

%post
/sbin/chkconfig --add amavisd-milter

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service amavisd-milter stop &>/dev/null || :
    /sbin/chkconfig --del amavisd-milter
fi

%postun
if [ $1 -ne 0 ]; then
    /sbin/service amavisd-milter condrestart &>/dev/null || :
fi

%files
%defattr(-, root, root, 0755)
%config %{_initrddir}/amavisd-milter
%{_sbindir}/amavisd-milter

%attr(0644, root, root) %{_sysconfdir}/sysconfig/*
%config(noreplace) %{_sysconfdir}/sysconfig/amavisd-milter

%attr(0644, root, root) %{_mandir}/man8/*
%doc %{_mandir}/man8/amavisd-milter.8.*

%changelog
* Sun Jan 20 2013  Jo Rhett
- Created for version 1.5.0
