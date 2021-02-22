#!/bin/sh
# Db for temperature CPU
rrdtool create /opt/HBMonv2/sysinfo/tempC.rrd \
--step 300 \
DS:temp:GAUGE:600:0:100 \
RRA:AVERAGE:0.5:1:288 \
RRA:AVERAGE:0.5:3:672 \
RRA:MIN:0.5:1:288 \
RRA:MIN:0.5:3:672 \
RRA:MAX:0.5:1:288 \
RRA:MAX:0.5:3:672 \
RRA:LAST:0.5:1:288 \
RRA:LAST:0.5:3:672 

# Db for memory usage
rrdtool create /opt/HBMonv2/sysinfo/mem.rrd \
--step 300 \
DS:mem:GAUGE:600:0:100 \
RRA:AVERAGE:0.5:1:288 \
RRA:AVERAGE:0.5:3:672 \
RRA:MIN:0.5:1:288 \
RRA:MIN:0.5:3:672 \
RRA:MAX:0.5:1:288 \
RRA:MAX:0.5:3:672 \
RRA:LAST:0.5:1:288 \
RRA:LAST:0.5:3:672 

# Db for disk usage
rrdtool create /opt/HBMonv2/sysinfo/hdd.rrd \
--step 300 \
DS:hdd:GAUGE:600:0:100 \
RRA:AVERAGE:0.5:1:288 \
RRA:AVERAGE:0.5:3:672 \
RRA:MIN:0.5:1:288 \
RRA:MIN:0.5:3:672 \
RRA:MAX:0.5:1:288 \
RRA:MAX:0.5:3:672 \
RRA:LAST:0.5:1:288 \
RRA:LAST:0.5:3:672 

# Db for CPU load
rrdtool create /opt/HBMonv2/sysinfo/load.rrd -s 60 \
DS:load1:GAUGE:180:0:U \
DS:load5:GAUGE:180:0:U \
DS:load15:GAUGE:180:0:U \
DS:cpuuser:COUNTER:180:0:100 \
DS:cpunice:COUNTER:180:0:100 \
DS:cpusystem:COUNTER:180:0:100 \
RRA:AVERAGE:0.5:1:1440 \
RRA:AVERAGE:0.5:1440:1 \
RRA:MIN:0.5:1440:1 \
RRA:MAX:0.5:1440:1
