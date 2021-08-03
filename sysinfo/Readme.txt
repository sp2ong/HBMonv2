Monitoring system 
==================

You can use and install ezSM tool to monitor your server instead described below method. 
The ezSM you can download from: https://www.ezservermonitor.com/

   cd /var/www/html
   git clone https://github.com/shevabam/ezservermonitor-web.git
   mv ezservermonitor-web esm
   cd esm/conf/
   
   Edit file esm.config.json and read documentation about configuration: https://www.ezservermonitor.com/esm-web/documentation
   Edit file /var/www/html/buttons.html and change link from
   
   <a href="sysinfo.php"><button class="button link">&nbsp;System Info&nbsp;</button></a>
   to:
   <a target=_blank href="esm/"><button class="button link">&nbsp;System Info&nbsp;</button></a>
   
   or you can add to sysinfo.php below line <?php include_once 'buttons.html'; ?>  following html code:
   
   <div>
   <a target="_blank" href="esm/"><button class="button link">&nbsp;eZ Server Monitor&nbsp;</button></a>
   </div>

You can put in esm.config.json monitor services like HBMonitor, HBlink like:
 
    "services": {
        "show_port": false,
        "list": [
            {
                "name": "Web Server",
                "host": "localhost",
                "port": 80,
                "protocol": "tcp"
            },
            {
                "name": "HBMonitor",
                "host": "localhost",
                "port": 9000,
                "protocol": "tcp"
            },
            {
                "name": "HBLink",
                "host": "localhost",
                "port": 4321,
                "protocol": "tcp"
            }



====================================================
Alternative SYSInfo based on rrdtools and scripts
====================================================
Below is a description of how to monitor the system using rrdtools and scripts :

Install package:

   sudo apt-get install rrdtool -y
   
Change scripts to execute:

  chmod +x /opt/HBMonv2/sysinfo/cpu.sh
  chmod +x /opt/HBMonv2/sysinfo/graph.sh
  chmod +x /opt/HBMonv2/sysinfo/rrd-db.sh
  
Run script  create database

   cd /opt/HBMonv2/sysinfo
   ./rrd-db.sh 


Edit file
    
  /opt/HBMonv2/sysinfo/cpu.sh

Setup in WEB_PATH path to your web server html directory 
for example /var/www/html or /var/www/html/hbmon 
where is located your html files of HBMon

Edit file
    
  /opt/HBMonv2/sysinfo/graph.sh

Setup in WEB_PATH path to your web server html directory 
for example /var/www/html or /var/www/html/hbmon 
where is located your html files of HBMon


Setup temperature depend of your computer 
On raspberry pi or PC you can use sensors package to get temperature CPU

If you don't want to show temperature on the Pi, comment out the line that gets the temp

Copy file sysinfo-cron to /etc/cron.d/  and restart crontab
   /etc/init.d/cron restart
   

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

Please edit /etc/mrtg.cfg and change diretory to store image change WorkDir with
path to your webserver html directory where is html files for HBMon:

   WorkDir:/var/www/html/hbmon/img/mrtg
   
   or 
   
   WorkDir:/var/www/html/img/mrtg

Put below lines in section your network card 
and replace localhost_2 to your name network card as result cfgmaker generate in mrtg.cfg

 XSize[localhost_2]: 600 
 Options[localhost_2]: growright, bits
 Unscaled[localhost_2]: d

Tune MaxBytes value for exmample 50000 to set vertical scale graph

Please edit template file where is which graph you are want display /var/www/html/sysinfo.php
and check / verify name of img from mrtg: <img alt="" src="img/mrtg/localhost_2-day.png" />

