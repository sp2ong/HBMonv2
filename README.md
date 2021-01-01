

**HBmonitor is a "web dashboard" for HBlink by N0MJS.**

***This is version of HBMonitor V2 by SP2ONG 2019-2021***

I recommend not running HBmonitor on the same computer as HBlink3

HBmonitor tested on Debian v9 and v10

This is version HBMonitor V2 

    cd /opt
    git clone https://github.com/sp2ong/HBMonv2.git
    cd HBMonv2
    chmod +x install.sh
    ./install.sh
    cp config-SAMPLE.py config.py
    edit config.py and change what you necessary
    cp utils/hbmon.service /lib/systemd/system/
    systemctl enable hbmon
    systemctl start hbmon
    systemctl status hbmon
    forward TCP ports 8080 and 9000 in firewall
    
    If you use openbrige links, in config.py in OPB_FILTER enter NETWORK_ID to do not display unnecessary entries in LASTHEARD.
    
    Please remember the table lastherad displays only station transmissions that are longer than 2 seconds.
    
    If you don't want to have the lasherad list set in config.py :  
      LASTHEARD_INC = False
    
    If you want to have more than the last 15 entries in the Lastherad table
    change in the monitor.py file line from
      if n == 15:
    to for example:
      if n == 20:

    I recommend using the following settings:
        WEB_AUTH = True
      in config.py and set a proper username and password in:
        WEB_USER = 'hblink'
        WEB_PASS = 'hblink'
    will provide access to more information about masters / peers / oprnbridge / monitor for users who know access Information.

    The display of buttons configurations are in the templates / buttons.html file. Don't change the code in the first part that checks if you have WEB_AUTH settings in config.py
    If you want to add your own buttons put the code below the line
    <! --- Own buttons html code ->

    In config.py you can choose one of the predefined HBmonitor colors or define your own by entering the code in THEME_COLOR

    If not need monitor online rules (I am not recommend) please use in config.py BRIDGES_INC = False

---

**hbmonitor3 by KC1AWV**

Python 3 implementation of N0MJS HBmonitor for HBlink https://github.com/kc1awv/hbmonitor3 

---

Copyright (C) 2013-2018  Cortney T. Buffington, N0MJS <n0mjs@me.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

---


