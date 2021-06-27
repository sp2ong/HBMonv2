#!/usr/bin/env python3
#
###############################################################################
#   Copyright (C) 2016-2019  Cortney T. Buffington, N0MJS <n0mjs@me.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################
#
#   Python 3 port by Steve Miller, KC1AWV <smiller@kc1awv.net>
#
###############################################################################
###############################################################################
#
#   HBMonitor v2 (2021) Version by Waldek SP2ONG
#
###############################################################################

# Standard modules
import logging
import sys
import datetime

import os
import csv
from itertools import islice
from subprocess import check_call, CalledProcessError

# Twisted modules
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, task

import base64

# Autobahn provides websocket service under Twisted
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

# Specific functions to import from standard modules
from time import time, strftime, localtime
from pickle import loads
from binascii import b2a_hex as h
from os.path import getmtime
from collections import deque
from time import time

# Web templating environment
from jinja2 import Environment, PackageLoader, select_autoescape

# Utilities from K0USY Group sister project
from dmr_utils3.utils import int_id, try_download, bytes_4
from json import load as jload

# Configuration variables and constants
from config import *

# SP2ONG - Increase the value if HBlink link break occurs
NetstringReceiver.MAX_LENGTH = 500000000

# Opcodes for reporting protocol to HBlink
OPCODE = {
    'CONFIG_REQ': '\x00',
    'CONFIG_SND': '\x01',
    'BRIDGE_REQ': '\x02',
    'BRIDGE_SND': '\x03',
    'CONFIG_UPD': '\x04',
    'BRIDGE_UPD': '\x05',
    'LINK_EVENT': '\x06',
    'BRDG_EVENT': '\x07',
    }

# Global Variables:
CONFIG      = {}
CTABLE      = {'MASTERS': {}, 'PEERS': {}, 'OPENBRIDGES': {}, 'SETUP': {}}
BRIDGES     = {}
BTABLE      = {'BRIDGES': {}, 'SETUP': {}}
#BTABLE['BRIDGES'] = {}
BRIDGES_RX  = ''
CONFIG_RX   = ''
LOGBUF      = deque(100*[''], 100)

RED         = 'ff6600'
BLACK       = '000000'
GREEN       = '90EE90'
GREEN2      = '008000'
BLUE        = '0000ff'
ORANGE      = 'ff8000'
WHITE       = 'ffffff'
WHITE2      = 'f9f9f9f9'
YELLOW      = 'fffccd'

# Define setup setings
CTABLE['SETUP']['LASTHEARD'] = LASTHEARD_INC
BTABLE['SETUP']['BRIDGES'] = BRIDGES_INC

# create empty systems list
sys_list = []

# OPB Filter for lastheard
def get_opbf():
   if len(OPB_FILTER) !=0:
       mylist = OPB_FILTER.replace(' ','').split(',')
   else:
       mylist = []
   return mylist

# For importing HTML templates
def get_template(_file):
    with open(_file, 'r') as html:
        return html.read()

# LONG VERSION - MAKES A FULL DICTIONARY OF INFORMATION BASED ON TYPE OF ALIAS FILE
# BASED ON DOWNLOADS FROM RADIOID.NET     
# moved from dmr_utils3
def mk_full_id_dict(_path, _file, _type):
    _dict = {}
    try:
        with open(_path+_file, 'r', encoding='latin1') as _handle:
            records = jload(_handle)
            if 'count' in [*records]:
                records.pop('count')
            records = records[[*records][0]]
            _handle.close
            if _type == 'peer':
                for record in records:
                    try:
                        _dict[int(record['id'])] = {
                            'CALLSIGN': record['callsign'],
                            'CITY': record['city'],
                            'STATE': record['state'],
                            'COUNTRY': record['country'],
                            'FREQ': record['frequency'],
                            'CC': record['color_code'],
                            'OFFSET': record['offset'],
                            'LINKED': record['ts_linked'],
                            'TRUSTEE': record['trustee'],
                            'NETWORK': record['ipsc_network']
                        }
                    except:
                        pass
            elif _type == 'subscriber':
                for record in records:
                    # Try to craete a string name regardless of existing data
                    if (('surname' in record.keys()) and ('fname'in record.keys())):
                        _name = str(record['fname'])
                    elif 'fname' in record.keys():
                        _name = str(record['fname'])
                    elif 'surname' in record.keys():
                        _name = str(record['surname'])
                    else:
                        _name = 'NO NAME'
                    # Make dictionary entry, if any of the information below isn't in the record, it wil be skipped
                    try:
                        _dict[int(record['id'])] = {
                            'CALLSIGN': record['callsign'],
                            'NAME': _name,
                            'CITY': record['city'],
                            'STATE': record['state'],
                            'COUNTRY': record['country']
                        }
                    except:
                        pass
            elif _type == 'tgid':
                for record in records:
                    try:
                        _dict[int(record['id'])] = {
                            'NAME': record['callsign']
                        }
                    except:
                        pass
        return _dict
    except IOError:
        return _dict

# THESE ARE THE SAME THING FOR LEGACY PURPOSES
# moved from dmr_urils3
def get_alias(_id, _dict, *args):
    if type(_id) == bytes:
        _id = int_id(_id)
    if _id in _dict:
        if args:
            retValue = []
            for _item in args:
                try:
                    retValue.append(_dict[_id][_item])
                except TypeError:
                    return _dict[_id]
            return retValue
        else:
            return _dict[_id]
    return _id

# Alias string processor
def alias_string(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'CITY', 'STATE')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return alias

def alias_short(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'NAME')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return str(alias)

def alias_call(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return str(alias)

def alias_tgid(_id, _dict):
    alias = get_alias(_id, _dict, 'NAME')
    if type(alias) == list:
        return str(alias[0])
    else:
        return str(" ")

# Return friendly elapsed time from time in seconds.
def since(_time):
    now = int(time())
    _time = now - int(_time)
    seconds = _time % 60
    minutes = int(_time/60) % 60
    hours = int(_time/60/60) % 24
    days = int(_time/60/60/24)
    if days:
        return '{}d {}h'.format(days, hours)
    elif hours:
        return '{}h {}m'.format(hours, minutes)
    elif minutes:
        return '{}m {}s'.format(minutes, seconds)
    else:
        return '{}s'.format(seconds)

def cleanTE():
##################################################
# Cleaning entries in tables - Timeout (5 min) 
#
    timeout = datetime.datetime.now().timestamp()

    for system in CTABLE['MASTERS']:
        for peer in CTABLE['MASTERS'][system]['PEERS']:
            for timeS in range(1,3):
              if CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TS']:
                ts = CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TIMEOUT']
                td = ts - timeout if ts > timeout else timeout - ts
                td = int(round(abs((td)) / 60))
                if td > 3:
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TS'] = False
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['COLOR'] = BLACK
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['BGCOLOR'] = WHITE2
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TYPE'] = ''
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['SUB'] = ''
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['SRC'] = ''
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['DEST'] = ''

    for system in CTABLE['PEERS']:
        for timeS in range(1,3):
            if CTABLE['PEERS'][system][timeS]['TS']:
              ts = CTABLE['PEERS'][system][timeS]['TIMEOUT']
              td = ts - timeout if ts > timeout else timeout - ts
              td = int(round(abs((td)) / 60))
              if td > 3:
                 CTABLE['PEERS'][system][timeS]['TS'] = False
                 CTABLE['PEERS'][system][timeS]['COLOR'] = BLACK
                 CTABLE['PEERS'][system][timeS]['BGCOLOR'] = WHITE2
                 CTABLE['PEERS'][system][timeS]['TYPE'] = ''
                 CTABLE['PEERS'][system][timeS]['SUB'] = ''
                 CTABLE['PEERS'][system][timeS]['SRC'] = ''
                 CTABLE['PEERS'][system][timeS]['DEST'] = ''

    for system in CTABLE['OPENBRIDGES']:
        for streamId in list(CTABLE['OPENBRIDGES'][system]['STREAMS']):
            ts = CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId][3]
            td = ts - timeout if ts > timeout else timeout - ts
            td = int(round(abs((td)) / 60))
            if td > 3:
                 del CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId]

                    
def add_hb_peer(_peer_conf, _ctable_loc, _peer):
    _ctable_loc[int_id(_peer)] = {}
    _ctable_peer = _ctable_loc[int_id(_peer)]

    # if the Frequency is 000.xxx assume it's not an RF peer, otherwise format the text fields
    # (9 char, but we are just software)  see https://wiki.brandmeister.network/index.php/Homebrew/example/php2
    
    if _peer_conf['TX_FREQ'].strip().isdigit() and _peer_conf['RX_FREQ'].strip().isdigit() and str(type(_peer_conf['TX_FREQ'])).find("bytes") != -1 and str(type(_peer_conf['RX_FREQ'])).find("bytes") != -1:
        if _peer_conf['TX_FREQ'][:3] == b'000' or _peer_conf['TX_FREQ'][:1] == b'0' or _peer_conf['RX_FREQ'][:3] == b'000' or _peer_conf['RX_FREQ'][:1] == b'0':
            _ctable_peer['TX_FREQ'] = 'N/A'
            _ctable_peer['RX_FREQ'] = 'N/A'
        else:
            _ctable_peer['TX_FREQ'] = _peer_conf['TX_FREQ'][:3].decode('utf-8') + '.' + _peer_conf['TX_FREQ'][3:7].decode('utf-8') + ' MHz'
            _ctable_peer['RX_FREQ'] = _peer_conf['RX_FREQ'][:3].decode('utf-8') + '.' + _peer_conf['RX_FREQ'][3:7].decode('utf-8') + ' MHz'
    else:
        _ctable_peer['TX_FREQ'] = 'N/A'
        _ctable_peer['RX_FREQ'] = 'N/A'      
    # timeslots are kinda complicated too. 0 = none, 1 or 2 mean that one slot, 3 is both, and anything else it considered DMO
    # Slots (0, 1=1, 2=2, 1&2=3 Duplex, 4=Simplex) see https://wiki.brandmeister.network/index.php/Homebrew/example/php2
    
    if (_peer_conf['SLOTS'] == b'0'):
        _ctable_peer['SLOTS'] = 'NONE'
    elif (_peer_conf['SLOTS'] == b'1' or _peer_conf['SLOTS'] == b'2'):
        _ctable_peer['SLOTS'] = _peer_conf['SLOTS'].decode('utf-8')
    elif (_peer_conf['SLOTS'] == b'3'):
        _ctable_peer['SLOTS'] = 'Duplex'
    else:
        _ctable_peer['SLOTS'] = 'Simplex'

    # Simple translation items
    if str(type(_peer_conf['PACKAGE_ID'])).find("bytes") != -1:
       _ctable_peer['PACKAGE_ID'] = _peer_conf['PACKAGE_ID'].decode('utf-8')
    else:
       _ctable_peer['PACKAGE_ID'] = _peer_conf['PACKAGE_ID']

    if str(type(_peer_conf['SOFTWARE_ID'])).find("bytes") != -1:
       _ctable_peer['SOFTWARE_ID'] = _peer_conf['SOFTWARE_ID'].decode('utf-8')
    else:
       _ctable_peer['SOFTWARE_ID'] = _peer_conf['SOFTWARE_ID']

    if str(type(_peer_conf['LOCATION'])).find("bytes") != -1:
       _ctable_peer['LOCATION'] = _peer_conf['LOCATION'].decode('utf-8').strip()
    else:
       _ctable_peer['LOCATION'] = _peer_conf['LOCATION']

    if str(type(_peer_conf['DESCRIPTION'])).find("bytes") != -1:
       _ctable_peer['DESCRIPTION'] = _peer_conf['DESCRIPTION'].decode('utf-8').strip()
    else:
       _ctable_peer['DESCRIPTION'] = _peer_conf['DESCRIPTION']

    if str(type(_peer_conf['URL'])).find("bytes") != -1:
       _ctable_peer['URL'] = _peer_conf['URL'].decode('utf-8').strip()
    else:
       _ctable_peer['URL'] = _peer_conf['URL']
       
    if str(type(_peer_conf['CALLSIGN'])).find("bytes") != -1:
       _ctable_peer['CALLSIGN'] = _peer_conf['CALLSIGN'].decode('utf-8').strip()
    else:
       _ctable_peer['CALLSIGN'] = _peer_conf['CALLSIGN']
    
    if str(type(_peer_conf['COLORCODE'])).find("bytes") != -1:
       _ctable_peer['COLORCODE'] = _peer_conf['COLORCODE'].decode('utf-8').strip()
    else:    
       _ctable_peer['COLORCODE'] = _peer_conf['COLORCODE']
    
    _ctable_peer['CONNECTION'] = _peer_conf['CONNECTION']
    _ctable_peer['CONNECTED'] = since(_peer_conf['CONNECTED'])
    
    _ctable_peer['IP'] = _peer_conf['IP']
    _ctable_peer['PORT'] = _peer_conf['PORT']
    
    #_ctable_peer['LAST_PING'] = _peer_conf['LAST_PING']

    # SLOT 1&2 - for real-time montior: make the structure for later use
    for ts in range(1,3):
        _ctable_peer[ts]= {}
        _ctable_peer[ts]['COLOR'] = ''
        _ctable_peer[ts]['BGCOLOR'] = ''
        _ctable_peer[ts]['TS'] = ''
        _ctable_peer[ts]['TYPE'] = ''
        _ctable_peer[ts]['SUB'] = ''
        _ctable_peer[ts]['SRC'] = ''
        _ctable_peer[ts]['DEST'] = ''

######################################################################
#
# Build the HBlink connections table
#

def build_hblink_table(_config, _stats_table):
    for _hbp, _hbp_data in list(_config.items()):
        if _hbp_data['ENABLED'] == True:

            # Process Master Systems
            if _hbp_data['MODE'] == 'MASTER':
                _stats_table['MASTERS'][_hbp] = {}
                if _hbp_data['REPEAT']:
                    _stats_table['MASTERS'][_hbp]['REPEAT'] = "repeat"
                else:
                    _stats_table['MASTERS'][_hbp]['REPEAT'] = "isolate"
                _stats_table['MASTERS'][_hbp]['PEERS'] = {}
                for _peer in _hbp_data['PEERS']:
                    add_hb_peer(_hbp_data['PEERS'][_peer], _stats_table['MASTERS'][_hbp]['PEERS'], _peer)

            # Process Peer Systems
            elif (_hbp_data['MODE'] == 'XLXPEER' or _hbp_data['MODE'] == 'PEER') and HOMEBREW_INC:
                _stats_table['PEERS'][_hbp] = {}
                _stats_table['PEERS'][_hbp]['MODE'] = _hbp_data['MODE']

                if str(type(_hbp_data['LOCATION'])).find("bytes") != -1:
                     _stats_table['PEERS'][_hbp]['LOCATION'] = _hbp_data['LOCATION'].decode('utf-8').strip()
                else:
                     _stats_table['PEERS'][_hbp]['LOCATION'] = _hbp_data['LOCATION']
                     
                if str(type(_hbp_data['DESCRIPTION'])).find("bytes") != -1:
                     _stats_table['PEERS'][_hbp]['DESCRIPTION'] = _hbp_data['DESCRIPTION'].decode('utf-8').strip()
                else:
                     _stats_table['PEERS'][_hbp]['DESCRIPTION'] = _hbp_data['DESCRIPTION']
                     
                if str(type(_hbp_data['URL'])).find("bytes") != -1:
                     _stats_table['PEERS'][_hbp]['URL'] = _hbp_data['DESCRIPTION'].decode('utf-8').strip()
                else:
                     _stats_table['PEERS'][_hbp]['URL'] = _hbp_data['DESCRIPTION']

                if str(type(_hbp_data['CALLSIGN'])).find("bytes") != -1:
                     _stats_table['PEERS'][_hbp]['CALLSIGN'] = _hbp_data['CALLSIGN'].decode('utf-8').strip()
                else:
                     _stats_table['PEERS'][_hbp]['CALLSIGN'] = _hbp_data['CALLSIGN']

                _stats_table['PEERS'][_hbp]['RADIO_ID'] = int_id(_hbp_data['RADIO_ID'])
                _stats_table['PEERS'][_hbp]['MASTER_IP'] = _hbp_data['MASTER_IP']
                _stats_table['PEERS'][_hbp]['MASTER_PORT'] = _hbp_data['MASTER_PORT']
                _stats_table['PEERS'][_hbp]['STATS'] = {}
                if _stats_table['PEERS'][_hbp]['MODE'] == 'XLXPEER': 
                    _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _hbp_data['XLXSTATS']['CONNECTION']
                    if _hbp_data['XLXSTATS']['CONNECTION'] == "YES":
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_hbp_data['XLXSTATS']['CONNECTED'])
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _hbp_data['XLXSTATS']['PINGS_SENT']
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _hbp_data['XLXSTATS']['PINGS_ACKD']
                    else:
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0
                else:
                    _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _hbp_data['STATS']['CONNECTION']
                    if _hbp_data['STATS']['CONNECTION'] == "YES":
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_hbp_data['STATS']['CONNECTED'])
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _hbp_data['STATS']['PINGS_SENT']
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _hbp_data['STATS']['PINGS_ACKD']
                    else:
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0
                if _hbp_data['SLOTS'] == b'0':
                    _stats_table['PEERS'][_hbp]['SLOTS'] = 'NONE'
                elif _hbp_data['SLOTS'] == b'1' or _hbp_data['SLOTS'] == b'2':
                    _stats_table['PEERS'][_hbp]['SLOTS'] = _hbp_data['SLOTS'].decode('utf-8')
                elif _hbp_data['SLOTS'] == b'3':
                    _stats_table['PEERS'][_hbp]['SLOTS'] = '1&2'
                else:
                    _stats_table['PEERS'][_hbp]['SLOTS'] = 'DMO'
                   # SLOT 1&2 - for real-time montior: make the structure for later use

                for ts in range(1,3):
                    _stats_table['PEERS'][_hbp][ts]= {}
                    _stats_table['PEERS'][_hbp][ts]['COLOR'] = ''
                    _stats_table['PEERS'][_hbp][ts]['BGCOLOR'] = ''
                    _stats_table['PEERS'][_hbp][ts]['TS'] = ''
                    _stats_table['PEERS'][_hbp][ts]['TYPE'] = ''
                    _stats_table['PEERS'][_hbp][ts]['SUB'] = ''
                    _stats_table['PEERS'][_hbp][ts]['SRC'] = ''
                    _stats_table['PEERS'][_hbp][ts]['DEST'] = ''


            # Process OpenBridge systems
            elif _hbp_data['MODE'] == 'OPENBRIDGE':
                _stats_table['OPENBRIDGES'][_hbp] = {}
                _stats_table['OPENBRIDGES'][_hbp]['NETWORK_ID'] = int_id(_hbp_data['NETWORK_ID'])
                _stats_table['OPENBRIDGES'][_hbp]['TARGET_IP'] = _hbp_data['TARGET_IP']
                _stats_table['OPENBRIDGES'][_hbp]['TARGET_PORT'] = _hbp_data['TARGET_PORT']
                _stats_table['OPENBRIDGES'][_hbp]['STREAMS'] = {}

    #return(_stats_table)

def update_hblink_table(_config, _stats_table):
    # Is there a system in HBlink's config monitor doesn't know about?
    for _hbp in _config:
        if _config[_hbp]['MODE'] == 'MASTER':
            for _peer in _config[_hbp]['PEERS']:
                if int_id(_peer) not in _stats_table['MASTERS'][_hbp]['PEERS'] and _config[_hbp]['PEERS'][_peer]['CONNECTION'] == 'YES':
                    logger.info('Adding peer to CTABLE that has registerred: %s', int_id(_peer))
                    add_hb_peer(_config[_hbp]['PEERS'][_peer], _stats_table['MASTERS'][_hbp]['PEERS'], _peer)

    # Is there a system in monitor that's been removed from HBlink's config?
    for _hbp in _stats_table['MASTERS']:
        remove_list = []
        if _config[_hbp]['MODE'] == 'MASTER':
            for _peer in _stats_table['MASTERS'][_hbp]['PEERS']:
                if bytes_4(_peer) not in _config[_hbp]['PEERS']:
                    remove_list.append(_peer)

            for _peer in remove_list:
                logger.info('Deleting stats peer not in hblink config: %s', _peer)
                del (_stats_table['MASTERS'][_hbp]['PEERS'][_peer])

    # Update connection time
    for _hbp in _stats_table['MASTERS']:
        for _peer in _stats_table['MASTERS'][_hbp]['PEERS']:
            if bytes_4(_peer) in _config[_hbp]['PEERS']:
                _stats_table['MASTERS'][_hbp]['PEERS'][_peer]['CONNECTED'] = since(_config[_hbp]['PEERS'][bytes_4(_peer)]['CONNECTED'])

    for _hbp in _stats_table['PEERS']:
        if _stats_table['PEERS'][_hbp]['MODE'] == 'XLXPEER':
            if _config[_hbp]['XLXSTATS']['CONNECTION'] == "YES":
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_config[_hbp]['XLXSTATS']['CONNECTED'])
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['XLXSTATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _config[_hbp]['XLXSTATS']['PINGS_SENT']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _config[_hbp]['XLXSTATS']['PINGS_ACKD']
            else:
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['XLXSTATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0
        else:
            if _config[_hbp]['STATS']['CONNECTION'] == "YES":
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_config[_hbp]['STATS']['CONNECTED'])
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['STATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _config[_hbp]['STATS']['PINGS_SENT']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _config[_hbp]['STATS']['PINGS_ACKD']
            else:
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['STATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0
    
    cleanTE()
    build_stats()

######################################################################
#
# CONFBRIDGE TABLE FUNCTIONS
#

def build_bridge_table(_bridges):
    _stats_table = {}
    _now = time()
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(_now))

    for _bridge, _bridge_data in list(_bridges.items()):
        _stats_table[_bridge] = {}

        for system in _bridges[_bridge]:
            _stats_table[_bridge][system['SYSTEM']] = {}
            _stats_table[_bridge][system['SYSTEM']]['TS'] = system['TS']
            _stats_table[_bridge][system['SYSTEM']]['TGID'] = int_id(system['TGID'])

            if system['TO_TYPE'] == 'ON' or system['TO_TYPE'] == 'OFF':
                if system['TIMER'] - _now > 0:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = int(system['TIMER'] - _now)
                else:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'Expired'
                if system['TO_TYPE'] == 'ON':
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Disconnect'
                else:
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Connect'
            else:
                _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'N/A'
                _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'None'

            if system['ACTIVE'] == True:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Connected'
                _stats_table[_bridge][system['SYSTEM']]['COLOR'] = BLACK
                _stats_table[_bridge][system['SYSTEM']]['BGCOLOR'] = GREEN
            elif system['ACTIVE'] == False:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Disconnected'
                _stats_table[_bridge][system['SYSTEM']]['COLOR'] = WHITE
                _stats_table[_bridge][system['SYSTEM']]['BGCOLOR'] = RED

            for i in range(len(system['ON'])):
                system['ON'][i] = str(int_id(system['ON'][i]))

            _stats_table[_bridge][system['SYSTEM']]['TRIG_ON'] = ', '.join(system['ON'])

            for i in range(len(system['OFF'])):
                system['OFF'][i] = str(int_id(system['OFF'][i]))

            _stats_table[_bridge][system['SYSTEM']]['TRIG_OFF'] = ', '.join(system['OFF'])
    return _stats_table

######################################################################
#
# BUILD HBlink AND CONFBRIDGE TABLES FROM CONFIG/BRIDGES DICTS
#          THIS CURRENTLY IS A TIMED CALL
#

build_time = time()
def build_stats():
    global build_time
    now = time()
    if True: #now > build_time + 1:
        if CONFIG:
             main = 'i' + itemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])
             dashboard_server.broadcast(main)
             peers = 'p' + ptemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])
             dashboard_server.broadcast(peers)
             masters = 'c' + ctemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'],emaster=EMPTY_MASTERS)
             dashboard_server.broadcast(masters)
             opb = 'o'+ otemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])
             dashboard_server.broadcast(opb)
        if BRIDGES and BRIDGES_INC and BTABLE['SETUP']['BRIDGES']:
            bridges = 'b' + btemplate.render(_table=BTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])
            dashboard_server.broadcast(bridges)
        build_time = now


def timeout_clients():
    now = time()
    try:
        for client in dashboard_server.clients:
            if dashboard_server.clients[client] + CLIENT_TIMEOUT < now:
                logger.info('TIMEOUT: disconnecting client %s', dashboard_server.clients[client])
                try:
                    dashboard.sendClose(client)
                except Exception as e:
                    logger.error('Exception caught parsing client timeout %s', e)
    except:
        logger.info('CLIENT TIMEOUT: List does not exist, skipping. If this message persists, contact the developer')


def rts_update(p):
    callType = p[0]
    action = p[1]
    trx = p[2]
    system = p[3]
    streamId = p[4]
    sourcePeer = int(p[5])
    sourceSub = int(p[6])
    timeSlot = int(p[7])
    destination = int(p[8])
    timeout = datetime.datetime.now().timestamp()
    
    if system in CTABLE['MASTERS']:
        for peer in CTABLE['MASTERS'][system]['PEERS']:
            if sourcePeer == peer:
                bgcolor = RED
                crxstatus = "RX"
                color = WHITE
            else:
                bgcolor = GREEN
                crxstatus = "TX"
                color = BLACK

            if action == 'START':
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TIMEOUT'] = timeout
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TS'] = True
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['COLOR'] = color
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['BGCOLOR'] = bgcolor
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TYPE'] = callType
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SUB'] = '{} ({})'.format(alias_short(sourceSub, subscriber_ids), sourceSub)
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['CALL'] = '{}'.format(alias_call(sourceSub, subscriber_ids))
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SRC'] = peer
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['DEST'] = 'TG {}&nbsp;&nbsp;&nbsp;&nbsp;{}'.format(destination,alias_tgid(destination,talkgroup_ids))    
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TG'] = 'TG&nbsp;{}'.format(destination)    
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TRX'] = crxstatus
            if action == 'END':
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TS'] = False
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['COLOR'] = BLACK
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['BGCOLOR'] = WHITE2
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TYPE'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SUB'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['CALL'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SRC'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['DEST'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TG'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TRX'] = ''

    if system in CTABLE['OPENBRIDGES']:
        if action == 'START':
            CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId] = (trx, alias_call(sourceSub, subscriber_ids),'{}'.format(destination),timeout)
        if action == 'END':
            if streamId in CTABLE['OPENBRIDGES'][system]['STREAMS']:
                del CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId]

    if system in CTABLE['PEERS']:
        bgcolor = GREEN
        if trx == 'RX':
            bgcolor = RED
            prxstatus = "RX"
            color = WHITE
        else:
            bgcolor = GREEN
            prxstatus = "TX"
            color = BLACK

        if action == 'START':
            CTABLE['PEERS'][system][timeSlot]['TIMEOUT'] = timeout
            CTABLE['PEERS'][system][timeSlot]['TS'] = True
            CTABLE['PEERS'][system][timeSlot]['COLOR'] = color
            CTABLE['PEERS'][system][timeSlot]['BGCOLOR'] = bgcolor
            CTABLE['PEERS'][system][timeSlot]['SUB'] = '{} ({})'.format(alias_short(sourceSub, subscriber_ids), sourceSub)
            CTABLE['PEERS'][system][timeSlot]['CALL'] = '{}'.format(alias_call(sourceSub, subscriber_ids))
            CTABLE['PEERS'][system][timeSlot]['SRC'] = sourcePeer
            CTABLE['PEERS'][system][timeSlot]['DEST'] = 'TG {}&nbsp;&nbsp;&nbsp;&nbsp;{}'.format(destination,alias_tgid(destination,talkgroup_ids))
            CTABLE['PEERS'][system][timeSlot]['TG'] = 'TG&nbsp;{}'.format(destination)
            CTABLE['PEERS'][system][timeSlot]['TRX'] = prxstatus
        if action == 'END':
            CTABLE['PEERS'][system][timeSlot]['TS'] = False
            CTABLE['PEERS'][system][timeSlot]['COLOR'] = BLACK
            CTABLE['PEERS'][system][timeSlot]['BGCOLOR'] = WHITE2
            CTABLE['PEERS'][system][timeSlot]['TYPE'] = ''
            CTABLE['PEERS'][system][timeSlot]['SUB'] = ''
            CTABLE['PEERS'][system][timeSlot]['CALL'] = ''
            CTABLE['PEERS'][system][timeSlot]['SRC'] = ''
            CTABLE['PEERS'][system][timeSlot]['DEST'] = ''
            CTABLE['PEERS'][system][timeSlot]['TG'] = ''
            CTABLE['PEERS'][system][timeSlot]['TRX'] = ''

    build_stats()

######################################################################
#
# PROCESS INCOMING MESSAGES AND TAKE THE CORRECT ACTION DEPENING ON
#    THE OPCODE
#

def process_message(_bmessage):
    global CTABLE, CONFIG, BRIDGES, CONFIG_RX, BRIDGES_RX, BRIDGES_INC
    _message = _bmessage.decode('utf-8', 'ignore')
    opcode = _message[:1]
    _now = strftime('%Y-%m-%d %H:%M:%S %Z', localtime(time()))

    if opcode == OPCODE['CONFIG_SND']:
        logging.debug('got CONFIG_SND opcode')
        CONFIG = load_dictionary(_bmessage)
        CONFIG_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        if CTABLE['MASTERS']:
            update_hblink_table(CONFIG, CTABLE)
        else:
            build_hblink_table(CONFIG, CTABLE)

    elif opcode == OPCODE['BRIDGE_SND']:
        logging.debug('got BRIDGE_SND opcode')
        BRIDGES = load_dictionary(_bmessage)
        BRIDGES_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        if BRIDGES_INC and BTABLE['SETUP']['BRIDGES']:
           BTABLE['BRIDGES'] = build_bridge_table(BRIDGES)

    elif opcode == OPCODE['LINK_EVENT']:
        logging.info('LINK_EVENT Received: {}'.format(repr(_message[1:])))

    elif opcode == OPCODE['BRDG_EVENT']:
        logging.info('BRIDGE EVENT: {}'.format(repr(_message[1:])))
        p = _message[1:].split(",")
        rts_update(p)
        opbfilter = get_opbf()
        if p[0] == 'GROUP VOICE' and p[2] != 'TX' and p[5] not in opbfilter:
            if p[1] == 'END':
                start_sys=0
                for x in sys_list:
                  if x[0]== p[3] and x[1] == p[4]:
                     sys_list.pop()
                     start_sys=1
                     break
            if p[1] == 'END' and start_sys==1:
                log_message = '{} {} {}   SYS: {:8.8s} SRC_ID: {:9.9s} TS: {} TGID: {:7.7s} {:17.17s} SUB: {:9.9s}; {:18.18s} Time: {}s '.format(_now[10:19], p[0][6:], p[1], p[3], p[5], p[7],p[8],alias_tgid(int(p[8]),talkgroup_ids), p[6], alias_short(int(p[6]), subscriber_ids), int(float(p[9])))
                # log only to file if system is NOT OpenBridge event (not logging open bridge system, name depends on your OB definitions) AND transmit time is LONGER as 2sec (make sense for very short transmits)
                if LASTHEARD_INC:
                   # save QSOs to lastheared.log for which transmission duration is longer than 2 sec, 
                   # use >=0 instead of >2 if you want to record all activities
                   if int(float(p[9])) > 2: 
                      log_lh_message = '{},{},{},{},{},{},{},TS{},TG{},{},{},{}'.format(_now, p[9], p[0], p[1], p[3], p[5], alias_call(int(p[5]), subscriber_ids), p[7], p[8],alias_tgid(int(p[8]),talkgroup_ids),p[6], alias_short(int(p[6]), subscriber_ids))
                      lh_logfile = open(LOG_PATH+"lastheard.log", "a", encoding="UTF-8", errors="ignore")
                      lh_logfile.write(log_lh_message + '\n')
                      lh_logfile.close()
                      # Lastheard in Dashboard by SP2ONG
                      my_list=[]
                      n=0
                      f = open(PATH+"templates/lastheard.html", "w", encoding="UTF-8", errors="ignore")
                      f.write("<br><fieldset style=\"border-radius: 8px; background-color:#f0f0f0f0;margin-left:15px;margin-right:15px;font-size:14px;border-top-left-radius: 10px; border-top-right-radius: 10px;border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;\">\n")
                      f.write("<legend><b><font color=\"#000\">&nbsp;.: Lastheard :.&nbsp;</font></b></legend>\n")
                      f.write("<table style=\"width:100%; font: 10pt arial, sans-serif;background-color:#f1f1f1;\">\n")
                      f.write("<TR class=\"theme_color\" style=\" height: 32px;font: 10pt arial, sans-serif;\"><TH>Date</TH><TH>Time</TH><TH>Callsign (DMR-Id)</TH><TH>Name</TH><TH>TG#</TH><TH>TG Name</TH><TH>TX (s)</TH><TH>System</TH></TR>\n")
                      with open(LOG_PATH+"lastheard.log", "r", encoding="UTF-8", errors="ignore") as textfile:
                          for row in islice(reversed(list(csv.reader(textfile))),200):
                            duration=row[1]
                            dur=str(int(float(duration.strip())))
                            if row[10] not in my_list:
                               if row[11].strip().isdigit() or row[11] == "N0CALL" or row[11] == "NOCALL":
                                  qrz = "<b><font color=#464646>"+row[11]+"</font></b>"
                               else:
                                  qrz = "<a style=\"font: 9pt arial,sans-serif;font-weight:bold;color:#0066ff;\" target=\"_blank\" href=https://qrz.com/db/"+row[11]+">"+row[11]+"</a></b><span style=\"font: 7pt arial,sans-serif\"> ("+row[10]+")</span>"
                               if len(row) < 13:
                                   hline="<TR class=\"log\"><TD>"+row[0][:10]+"</TD><TD>"+row[0][11:16]+"</TD><TD>"+qrz+"</TD><TD><font color=#002d62><b></b></font></TD><TD><font color=#b5651d><b>"+row[8][2:]+"</b></font></TD><TD><font color=green><b>"+row[9]+"</b></font></TD><TD>"+dur+"</TD><TD>"+row[4]+"</TD></TR>"
                                   my_list.append(row[10])
                                   n += 1
                               else:
                                   hline="<TR class=\"log\"><TD>"+row[0][:10]+"</TD><TD>"+row[0][11:16]+"</TD><TD>"+qrz+"</TD><TD><font color=#002d62><b>"+row[12]+"</b></font></TD><TD><font color=#b5651d><b>"+row[8][2:]+"</b></font></TD><TD><font color=green><b>"+row[9]+"</b></font></TD><TD>"+dur+"</TD><TD>"+row[4]+"</TD></TR>"
                                   my_list.append(row[10])
                                   n += 1
                               f.write(hline+"\n")
                            # maximum number of lists in lastheard on the main page 
                            if n == 15:
                               break
                      f.write("</table></fieldset><br>")
                      f.close()
                # End of Lastheard
                # Removing obsolete entries from the sys_list (3 sec)
                deleteList=[]
                processNo = 0
                timeO = datetime.datetime.now().timestamp()
                for item in sys_list:
                   td = item[2] - timeO if item[2] > timeO else timeO - item[2]
                   td = int(round(abs((td)) / 60))
                   if td > 3:
                      deleteList.insert(0,processNo)
                   processNo +=1
                if len(deleteList) >0:
                   for item in deleteList:
                       del sys_list[item]
            elif p[1] == 'START':
                log_message = '{} {} {} SYS: {:8.8s} SRC_ID: {:9.9s} TS: {} TGID: {:7.7s} {:17.17s} SUB: {:9.9s}; {:18.18s}'.format(_now[10:19], p[0][6:], p[1], p[3], p[5], p[7],p[8], alias_tgid(int(p[8]),talkgroup_ids), p[6], alias_short(int(p[6]), subscriber_ids))
                timeST = datetime.datetime.now().timestamp()
                sys_list.append([p[3],p[4],timeST])
            elif p[1] == 'END' and start_sys==0:
                log_message = '{} {} {}   SYS: {:8.8s} SRC_ID: {:9.9s} TS: {} TGID: {:7.7s} {:17.17s} SUB: {:9.9s}; {:18.18s} Time: {}s '.format(_now[10:19], p[0][6:], p[1], p[3], p[5], p[7],p[8],alias_tgid(int(p[8]),talkgroup_ids), p[6], alias_short(int(p[6]), subscriber_ids), int(float(p[9])))
            elif p[1] == 'END WITHOUT MATCHING START':
                log_message = '{} {} {} on SYSTEM {:8.8s}: SRC_ID: {:9.9s} TS: {} TGID: {:7.7s} {:17.17s} SUB: {:9.9s}; {:18.18s}'.format(_now[10:19], p[0][6:], p[1], p[3], p[5], p[7], p[8],alias_tgid(int(p[8]),talkgroup_ids),p[6], alias_short(int(p[6]), subscriber_ids))
            else:
                log_message = '{} UNKNOWN GROUP VOICE LOG MESSAGE'.format(_now[10:19])

            dashboard_server.broadcast('l' + log_message)
            LOGBUF.append(log_message)

        else:
            logging.debug('{} UNKNOWN LOG MESSAGE'.format(_now[10:19]))

    else:
        logging.debug('got unknown opcode: {}, message: {}'.format(repr(opcode), repr(_message[1:])))

def load_dictionary(_message):
    data = _message[1:]
    return loads(data)
    logging.debug('Successfully decoded dictionary')

######################################################################
#
# COMMUNICATION WITH THE HBlink INSTANCE
#

class report(NetstringReceiver):
    def __init__(self):
        pass

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def stringReceived(self, data):
        process_message(data)


class reportClientFactory(ReconnectingClientFactory):
    def __init__(self):
        logging.info('reportClient object for connecting to HBlink.py created at: %s', self)

    def startedConnecting(self, connector):
        logging.info('Initiating Connection to Server.')
        if 'dashboard_server' in locals() or 'dashboard_server' in globals():
            dashboard_server.broadcast('q' + 'Connection to HBlink Established')

    def buildProtocol(self, addr):
        logging.info('Connected.')
        logging.info('Resetting reconnection delay')
        self.resetDelay()
        return report()

    def clientConnectionLost(self, connector, reason):
        CTABLE['MASTERS'].clear()
        CTABLE['PEERS'].clear()
        CTABLE['OPENBRIDGES'].clear()
        BTABLE['BRIDGES'].clear()
        logging.info('Lost connection.  Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        dashboard_server.broadcast('q' + 'Connection to HBlink Lost')

    def clientConnectionFailed(self, connector, reason):
        logging.info('Connection failed. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

######################################################################
#
# WEBSOCKET COMMUNICATION WITH THE DASHBOARD CLIENT
#

class dashboard(WebSocketServerProtocol):
    global INFO, MONITOR, OPENBRIDGE
    def onConnect(self, request):
        logging.info('Client connecting: %s', request.peer)

    def onOpen(self):
        #if BTABLE['SETUP']['BRIDGES']:
        #      ddbridges = True
        #else:
        #      ddbridges = False
        logging.info('WebSocket connection open.')
        self.factory.register(self)
        if BRIDGES and BRIDGES_INC and BTABLE['SETUP']['BRIDGES']:
           self.sendMessage(('b' + btemplate.render(_table=BTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])).encode('utf-8'))
        self.sendMessage(('c' + ctemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'],emaster=EMPTY_MASTERS)).encode('utf-8'))
        self.sendMessage(('p' + ptemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])).encode('utf-8'))
        self.sendMessage(('o' + otemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])).encode('utf-8'))
        self.sendMessage(('i' + itemplate.render(_table=CTABLE,dbridges=BTABLE['SETUP']['BRIDGES'])).encode('utf-8'))
        for _message in LOGBUF:
            if _message:
                _bmessage = ('l' + _message).encode('utf-8')
                self.sendMessage(_bmessage)
                
    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.info('Binary message received: %s bytes', len(payload))
        else:
            logging.info('Text message received: %s', payload)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def onClose(self, wasClean, code, reason):
        logging.info('WebSocket connection closed: %s', reason)

class dashboardFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = {}

    def register(self, client):
        if client not in self.clients:
            logging.info('registered client %s', client.peer)
            self.clients[client] = time()

    def unregister(self, client):
        if client in self.clients:
            logging.info('unregistered client %s', client.peer)
            del self.clients[client]

    def broadcast(self, msg):
        logging.debug('broadcasting message to: %s', self.clients)
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            logging.debug('message sent to %s', c.peer)

######################################################################
#

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename = (LOG_PATH + LOG_NAME),
        filemode='a',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logger = logging.getLogger(__name__)

    logging.info('monitor.py starting up')
    logger.info('\n\n\tCopyright (c) 2016, 2017, 2018, 2019\n\tThe Regents of the K0USY Group. All rights reserved.\n\n\tPython 3 port:\n\t2019 Steve Miller, KC1AWV <smiller@kc1awv.net>\n\n\tHBMonitor v2 SP2ONG 2019-2021\n\n')
    # Check lastheard.log 
    if os.path.isfile(LOG_PATH+"lastheard.log"):
      try:
         check_call("sed -i -e 's|\\x0||g' {}".format(LOG_PATH+"lastheard.log"), shell=True)
         logging.info('Check lastheard.log file')
      except CalledProcessError as err:
         print(err)
    # Download alias files
    result = try_download(PATH, PEER_FILE, PEER_URL, (FILE_RELOAD * 86400))
    logging.info(result)

    result = try_download(PATH, SUBSCRIBER_FILE, SUBSCRIBER_URL, (FILE_RELOAD * 86400))
    logging.info(result)

    # Make Alias Dictionaries
    peer_ids = mk_full_id_dict(PATH, PEER_FILE, 'peer')
    if peer_ids:
        logging.info('ID ALIAS MAPPER: peer_ids dictionary is available')

    subscriber_ids = mk_full_id_dict(PATH, SUBSCRIBER_FILE, 'subscriber')
    if subscriber_ids:
        logging.info('ID ALIAS MAPPER: subscriber_ids dictionary is available')

    talkgroup_ids = mk_full_id_dict(PATH, TGID_FILE, 'tgid')
    if talkgroup_ids:
        logging.info('ID ALIAS MAPPER: talkgroup_ids dictionary is available')

    local_subscriber_ids = mk_full_id_dict(PATH, LOCAL_SUB_FILE, 'subscriber')
    if local_subscriber_ids:
        logging.info('ID ALIAS MAPPER: local_subscriber_ids added to subscriber_ids dictionary')
        subscriber_ids.update(local_subscriber_ids)

    local_talkgroup_ids = mk_full_id_dict(PATH, LOCAL_TGID_FILE, 'tgid')
    if local_talkgroup_ids:
        logging.info('ID ALIAS MAPPER: local_talkgroup_ids added to talkgroup_ids dictionary')
        talkgroup_ids.update(local_talkgroup_ids)

    local_peer_ids = mk_full_id_dict(PATH, LOCAL_PEER_FILE, 'peer')
    if local_peer_ids:
        logging.info('ID ALIAS MAPPER: local_peer_ids added peer_ids dictionary')
        peer_ids.update(local_peer_ids)

    # Jinja2 Stuff
    env = Environment(
        loader=PackageLoader('monitor', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # define tables template
    itemplate = env.get_template('main_table.html')
    ptemplate = env.get_template('peers_table.html')
    ctemplate = env.get_template('masters_table.html')
    otemplate = env.get_template('opb_table.html')
    btemplate = env.get_template('bridge_table.html')

    # Start update loop
    update_stats = task.LoopingCall(build_stats)
    update_stats.start(FREQUENCY)

    # Start a timout loop
    if CLIENT_TIMEOUT > 0:
        timeout = task.LoopingCall(timeout_clients)
        timeout.start(10)

    # Connect to HBlink
    reactor.connectTCP(HBLINK_IP, HBLINK_PORT, reportClientFactory())
    

    # HBmonitor does not require the use of SSL as no "sensitive data" is sent to it but if you want to use SSL:
    # create websocket server to push content to clients via SSL https://
    # the web server apache2 should be configured with a signed certificate for example Letsencrypt
    # we need install pyOpenSSL required by twisted: pip3 install pyOpenSSL
    # and add load ssl module in line number 43: from twisted.internet import reactor, task, ssl
    #
    # put certificate https://letsencrypt.org/ used in apache server 
    #certificate = ssl.DefaultOpenSSLContextFactory('/etc/letsencrypt/live/hbmon.dmrserver.org/privkey.pem', '/etc/letsencrypt/live/hbmon.dmrserver.org/cert.pem')
    #dashboard_server = dashboardFactory('wss://*:9000')
    #dashboard_server.protocol = dashboard
    #reactor.listenSSL(9000, dashboard_server,certificate)

    # Create websocket server to push content to clients via http:// non SSL
    dashboard_server = dashboardFactory('ws://*:9000')
    dashboard_server.protocol = dashboard
    reactor.listenTCP(9000, dashboard_server)


    reactor.run()
