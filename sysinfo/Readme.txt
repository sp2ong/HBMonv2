Monitoring system 

Install package:

   sudo apt-get install rrdtool -y
   
Change scripts to execute:

  chmod +x /opt/HBMonv2/sysinfo/cpu.sh
  chmod +x /opt/HBMonv2/sysinfo/grap.sh
  chmod +x /opt/HBMonv2/sysinfo/rrd-db.sh
  
Run script  create database

  /opt/HBMonv2/sysinfo/rrd-db.sh 

Edit file
    
  /opt/HBMonv2/sysinfo/graph.sh

Setup temperature depend of your computer 
On raspberry pi or PC you can use sensors package to get temperature CPU

If not avilable set:

   tempcpu=false

For VPS set:

   tempcpu=false


Optional display network traffic
===============================

Instal package mrtg and snmp 

  sudo apt-get install mrtg snmp snmpd -y

Edit file

  /etc/snmp/snmpd.conf

and set as below


   rocommunity public  localhost 
   #rocommunity public  default    -V systemonly               
   #rocommunity6 public  default   -V systemonly


Restart snmpd

  systemctl restart snmpd


Create config for mrtg:

  cfgmaker -zero-speed=10000  public@localhost > /etc/mrtg.cfg

Please edit /etc/mrtg.cfg and change diretory to store image change WorkDir to:

   WorkDir:/opt/HBMonv2/img/mrtg

put below lines in section your netrwork card 
and replace localhost_2 to your name network card as result cfgmaker generate in mrtg.cfg

 XSize[localhost_2]: 600 
 Options[localhost_2]: growright, bits
 Unscaled[localhost_2]: d

Tune MaxBytes value for exmample 50000 to set vertical scale graph

Please edit template file where is which graph you are want display /opt/HBMonv2/templates/sysinfo_template.html



