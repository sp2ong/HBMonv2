#!/bin/bash

# Setup path web server directory where is html files of HBMon
WEB_PATH='/var/www/html/'

# Get values

# Temperature CPU (not working for VPS)

# Setup temperature for CPU ============


#For Raspberry PI, comment next 4 lines if you don't want temperature:

FILE=/sys/class/thermal/thermal_zone0/temp
if [[ -f "$FILE" ]]; then
tempC=`cat /sys/class/thermal/thermal_zone0/temp |awk '{printf("%.1f",$1/1000)}'`
fi

# For computers not like Raspberry PI install package 
# at install lm-sensors 
# and run: sensors-detect
# after this check result run command: sensors to see temperature CPU

if [ -z "$tempC" ] ; then
tempC=`sensors | grep -i "Core 0" | grep "$1" | sed -re "s/.*:[^+]*?[+]([.0-9]+)[ °]C.*/\1/g"`
fi

#=====================================

# Usage of hdd /
hdd=`df -h | awk '$NF=="/"{printf "%s",$5}'|sed 's/.$//'|awk '{printf("%.1f",$1)}'`

# Memory usage
mem=`free -m | awk 'NR==2{printf "%.1f", $3*100/$2 }'`

# CPU load
load=`/bin/sed "s/\([0-9]\\.[0-9]\\{2\\}\)\ \([0-9]\\.[0-9]\\{2\\}\)\ \([0-9]\\.[0-9]\\{2\\}\).*/\1:\2:\3/" < /proc/loadavg`:`/usr/bin/head -n 1 /proc/stat | /bin/sed "s/^cpu\ \+\([0-9]*\)\ \([0-9]*\)\ \([0-9]*\).*/\1:\2:\3/"`

# Get time
NOW=`date -u +%s`

# Update db =====================================================

if [ -n "$tempC" ] ; then
/usr/bin/rrdtool update /opt/HBMonv2/sysinfo/tempC.rrd $NOW:$tempC
fi

/usr/bin/rrdtool update /opt/HBMonv2/sysinfo/mem.rrd $NOW:$mem
/usr/bin/rrdtool update /opt/HBMonv2/sysinfo/hdd.rrd $NOW:$hdd
/usr/bin/rrdtool update /opt/HBMonv2/sysinfo/load.rrd $NOW:$load

# Generate images ================================================================


if [ -n "$tempC" ] ; then
# Temperature CPU
/usr/bin/rrdtool graph $WEB_PATH/img/tempC.png -t "Temperature CPU 24H - `/bin/date`" \
--rigid --alt-y-grid --alt-autoscale --units-exponent 0 \
-w 600 -h 70 --upper-limit 100 --vertical-label 'Temperature [C]' --slope-mode --start -86400 \
DEF:ave=/opt/HBMonv2/sysinfo/tempC.rrd:temp:AVERAGE \
CDEF:C=ave,100,GE,ave,0,IF AREA:C#7F0000: \
CDEF:D=ave,95,GE,ave,100,LT,ave,100,IF,0,IF AREA:D#9E0000: \
CDEF:E=ave,90,GE,ave,95,LT,ave,95,IF,0,IF AREA:E#BD0000: \
CDEF:F=ave,85,GE,ave,90,LT,ave,90,IF,0,IF AREA:F#DD0000: \
CDEF:G=ave,80,GE,ave,85,LT,ave,85,IF,0,IF AREA:G#FC0000: \
CDEF:H=ave,75,GE,ave,80,LT,ave,80,IF,0,IF AREA:H#FF1D00: \
CDEF:I=ave,70,GE,ave,75,LT,ave,75,IF,0,IF AREA:I#FC3D00: \
CDEF:J=ave,65,GE,ave,70,LT,ave,70,IF,0,IF AREA:J#FF5C00: \
CDEF:K=ave,60,GE,ave,65,LT,ave,65,IF,0,IF AREA:K#FF7C00: \
CDEF:L=ave,55,GE,ave,60,LT,ave,60,IF,0,IF AREA:L#FFBA00: \
CDEF:M=ave,50,GE,ave,55,LT,ave,55,IF,0,IF AREA:M#FFD900: \
CDEF:N=ave,45,GE,ave,50,LT,ave,50,IF,0,IF AREA:N#FFF900: \
CDEF:O=ave,40,GE,ave,45,LT,ave,45,IF,0,IF AREA:O#E5FF1A: \
CDEF:P=ave,35,GE,ave,40,LT,ave,40,IF,0,IF AREA:P#C6FF39: \
CDEF:Q=ave,30,GE,ave,35,LT,ave,35,IF,0,IF AREA:Q#A6FF58: \
CDEF:R=ave,25,GE,ave,30,LT,ave,30,IF,0,IF AREA:R#87FF78: \
CDEF:S=ave,20,GE,ave,25,LT,ave,25,IF,0,IF AREA:S#69FE96: \
CDEF:T=ave,15,GE,ave,20,LT,ave,20,IF,0,IF AREA:T#49FEB6: \
CDEF:U=ave,10,GE,ave,15,LT,ave,15,IF,0,IF AREA:U#2AFED5: \
CDEF:VV=ave,5,GE,ave,10,LT,ave,10,IF,0,IF AREA:VV#0BFFF4: \
CDEF:WW=ave,0,GE,ave,5,LT,ave,5,IF,0,IF AREA:WW#0BFFF4: \
CDEF:A=ave \
VDEF:V=ave,AVERAGE \
LINE1:ave \
LINE1:A#000000:Temperature \
DEF:tmax=/opt/HBMonv2/sysinfo/tempC.rrd:temp:MAX \
DEF:tmin=/opt/HBMonv2/sysinfo/tempC.rrd:temp:MIN \
'GPRINT:ave:LAST:Last\: %2.1lf C' \
'GPRINT:tmin:MIN:Minimum\: %2.1lf C' \
'GPRINT:tmax:MAX:Maximum\: %2.1lf C\j' >/dev/null
fi

# Memory usage 
/usr/bin/rrdtool graph $WEB_PATH/img/mem.png -t "Memory usage 24H - `grep MemTotal /proc/meminfo | awk '{printf "%.0f MB", $2/1024}'` - `/bin/date`" \
--rigid --alt-y-grid --alt-autoscale --units-exponent 0 \
-w 600 -h 70 --upper-limit 100 --vertical-label 'Memory usage [%]' --slope-mode --start -86400 \
DEF:ave=/opt/HBMonv2/sysinfo/mem.rrd:mem:AVERAGE \
CDEF:C=ave,100,GE,ave,0,IF AREA:C#7F0000: \
CDEF:D=ave,95,GE,ave,100,LT,ave,100,IF,0,IF AREA:D#9E0000: \
CDEF:E=ave,90,GE,ave,95,LT,ave,95,IF,0,IF AREA:E#BD0000: \
CDEF:F=ave,85,GE,ave,90,LT,ave,90,IF,0,IF AREA:F#DD0000: \
CDEF:G=ave,80,GE,ave,85,LT,ave,85,IF,0,IF AREA:G#FC0000: \
CDEF:H=ave,75,GE,ave,80,LT,ave,80,IF,0,IF AREA:H#FF1D00: \
CDEF:I=ave,70,GE,ave,75,LT,ave,75,IF,0,IF AREA:I#FC3D00: \
CDEF:J=ave,65,GE,ave,70,LT,ave,70,IF,0,IF AREA:J#FF5C00: \
CDEF:K=ave,60,GE,ave,65,LT,ave,65,IF,0,IF AREA:K#FF7C00: \
CDEF:L=ave,55,GE,ave,60,LT,ave,60,IF,0,IF AREA:L#FFBA00: \
CDEF:M=ave,50,GE,ave,55,LT,ave,55,IF,0,IF AREA:M#FFD900: \
CDEF:N=ave,45,GE,ave,50,LT,ave,50,IF,0,IF AREA:N#FFF900: \
CDEF:O=ave,40,GE,ave,45,LT,ave,45,IF,0,IF AREA:O#E5FF1A: \
CDEF:P=ave,35,GE,ave,40,LT,ave,40,IF,0,IF AREA:P#C6FF39: \
CDEF:Q=ave,30,GE,ave,35,LT,ave,35,IF,0,IF AREA:Q#A6FF58: \
CDEF:R=ave,25,GE,ave,30,LT,ave,30,IF,0,IF AREA:R#87FF78: \
CDEF:S=ave,20,GE,ave,25,LT,ave,25,IF,0,IF AREA:S#69FE96: \
CDEF:T=ave,15,GE,ave,20,LT,ave,20,IF,0,IF AREA:T#49FEB6: \
CDEF:U=ave,10,GE,ave,15,LT,ave,15,IF,0,IF AREA:U#2AFED5: \
CDEF:VV=ave,5,GE,ave,10,LT,ave,10,IF,0,IF AREA:VV#0BFFF4: \
CDEF:WW=ave,0,GE,ave,5,LT,ave,5,IF,0,IF AREA:WW#0BFFF4: \
CDEF:A=ave \
VDEF:V=ave,AVERAGE \
LINE1:ave \
LINE1:A#000000:Memory_usage_% \
DEF:tmax=/opt/HBMonv2/sysinfo/mem.rrd:mem:MAX \
DEF:tmin=/opt/HBMonv2/sysinfo/mem.rrd:mem:MIN \
'GPRINT:ave:LAST:Last\: %2.1lf ' \
'GPRINT:tmin:MIN:Minimum\: %2.1lf ' \
'GPRINT:tmax:MAX:Maximum\: %2.1lf \j' >/dev/null

# Disk usage 
/usr/bin/rrdtool graph $WEB_PATH/img/hdd.png -t "Disk usage 24H - Size: `df -h / |awk 'NR==2 { print $2 }'` - `/bin/date`" \
--rigid --alt-y-grid --alt-autoscale --units-exponent 0 \
-w 600 -h 70 --upper-limit 100 --vertical-label 'Disk usage [%]' --slope-mode --start -86400 \
DEF:ave=/opt/HBMonv2/sysinfo/hdd.rrd:hdd:AVERAGE \
CDEF:C=ave,100,GE,ave,0,IF AREA:C#7F0000: \
CDEF:D=ave,95,GE,ave,100,LT,ave,100,IF,0,IF AREA:D#9E0000: \
CDEF:E=ave,90,GE,ave,95,LT,ave,95,IF,0,IF AREA:E#BD0000: \
CDEF:F=ave,85,GE,ave,90,LT,ave,90,IF,0,IF AREA:F#DD0000: \
CDEF:G=ave,80,GE,ave,85,LT,ave,85,IF,0,IF AREA:G#FC0000: \
CDEF:H=ave,75,GE,ave,80,LT,ave,80,IF,0,IF AREA:H#FF1D00: \
CDEF:I=ave,70,GE,ave,75,LT,ave,75,IF,0,IF AREA:I#FC3D00: \
CDEF:J=ave,65,GE,ave,70,LT,ave,70,IF,0,IF AREA:J#FF5C00: \
CDEF:K=ave,60,GE,ave,65,LT,ave,65,IF,0,IF AREA:K#FF7C00: \
CDEF:L=ave,55,GE,ave,60,LT,ave,60,IF,0,IF AREA:L#FFBA00: \
CDEF:M=ave,50,GE,ave,55,LT,ave,55,IF,0,IF AREA:M#FFD900: \
CDEF:N=ave,45,GE,ave,50,LT,ave,50,IF,0,IF AREA:N#FFF900: \
CDEF:O=ave,40,GE,ave,45,LT,ave,45,IF,0,IF AREA:O#E5FF1A: \
CDEF:P=ave,35,GE,ave,40,LT,ave,40,IF,0,IF AREA:P#C6FF39: \
CDEF:Q=ave,30,GE,ave,35,LT,ave,35,IF,0,IF AREA:Q#A6FF58: \
CDEF:R=ave,25,GE,ave,30,LT,ave,30,IF,0,IF AREA:R#87FF78: \
CDEF:S=ave,20,GE,ave,25,LT,ave,25,IF,0,IF AREA:S#69FE96: \
CDEF:T=ave,15,GE,ave,20,LT,ave,20,IF,0,IF AREA:T#49FEB6: \
CDEF:U=ave,10,GE,ave,15,LT,ave,15,IF,0,IF AREA:U#2AFED5: \
CDEF:VV=ave,5,GE,ave,10,LT,ave,10,IF,0,IF AREA:VV#0BFFF4: \
CDEF:WW=ave,0,GE,ave,5,LT,ave,5,IF,0,IF AREA:WW#0BFFF4: \
CDEF:A=ave \
VDEF:V=ave,AVERAGE \
LINE1:ave \
LINE1:A#000000:Disk_usage_% \
DEF:tmax=/opt/HBMonv2/sysinfo/hdd.rrd:hdd:MAX \
DEF:tmin=/opt/HBMonv2/sysinfo/hdd.rrd:hdd:MIN \
'GPRINT:ave:LAST:Last\: %2.1lf ' \
'GPRINT:tmin:MIN:Minimum\: %2.1lf ' \
'GPRINT:tmax:MAX:Maximum\: %2.1lf \j' >/dev/null

