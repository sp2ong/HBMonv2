#!/bin/sh

# Setup web server directory where is html files HBMon
WEB_PATH='/var/www/html/'

# CPU load
load=`/bin/sed "s/\([0-9]\\.[0-9]\\{2\\}\)\ \([0-9]\\.[0-9]\\{2\\}\)\ \([0-9]\\.[0-9]\\{2\\}\).*/\1:\2:\3/" < /proc/loadavg`:`/usr/bin/head -n 1 /proc/stat | /bin/sed "s/^cpu\ \+\([0-9]*\)\ \([0-9]*\)\ \([0-9]*\).*/\1:\2:\3/"`

# Get time
NOW=`date -u +%s`

# Update db =====================================================

/usr/bin/rrdtool update /opt/HBMonv2/sysinfo/load.rrd $NOW:$load

# Generate images ================================================================


# CPU loads
/usr/bin/rrdtool graph $WEB_PATH/img/cpu.png \
-Y -r -u 100 -l 0 -L 5 -v "CPU usage" -w 600 -h 70 -t "CPU status 24H - `/bin/date`" \
-c ARROW\#000000 -x MINUTE:30:MINUTE:30:HOUR:1:0:%H \
DEF:user=/opt/HBMonv2/sysinfo/load.rrd:cpuuser:AVERAGE \
DEF:nice=/opt/HBMonv2/sysinfo/load.rrd:cpunice:AVERAGE \
DEF:sys=/opt/HBMonv2/sysinfo/load.rrd:cpusystem:AVERAGE \
CDEF:idle=100,user,nice,sys,+,+,- \
COMMENT:"	" \
AREA:user\#FF0000:"CPU user" \
STACK:nice\#000099:"CPU nice" \
STACK:sys\#FFFF00:"CPU system" \
STACK:idle\#00FF00:"CPU idle" \
COMMENT:"	\j" >/dev/null

