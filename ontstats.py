#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0
# Inspired from https://github.com/loiklo/huawei-onu-to-graphite

import requests
from base64 import b64encode
from influxdb import InfluxDBClient
from time import sleep

## Default
# ont_host     = "192.168.100.1"
# ont_username = "root"
# ont_password = "adminHW"

## Orange custom
# ont_host     = "192.168.4.254"
# ont_username = "root"
# ont_password = "admin"

# User vars

ont_host = '192.168.100.1'
ont_username = 'root'
ont_password = 'admin'
influx_host = 'grafana'
influx_db = 'ONT'

interval = 30   # NB: the ONT deauths after 60s, using lower values reuses the established HTTP session

wantedFields = set(['transOpticPower','revOpticPower','voltage','temperature','bias','LosStatus'])

# don't touch below this line

opticInfo = {
    'domain': None,
    'transOpticPower': None,
    'revOpticPower': None,
    'voltage': None,
    'temperature': None,
    'bias': None,
    'rfRxPower': None,
    'rfOutputPower': None,
    'VendorName': None,
    'VendorSN': None,   # used as tag
    'DateCode': None,
    'TxWaveLength': None,
    'RxWaveLength': None,
    'MaxTxDistance': None,
    'LosStatus': None,
    }

ont_urlprefix = 'http://' + ont_host

def cleanval(value):
    try:
        return float(value)
    except:
        value = value.strip()
        if not value:
            return None
        else:
            return value

def login(s):
  # Get token
    r = s.post(ont_urlprefix + '/asp/GetRandCount.asp')
    sid = r.text[-32:]
  # Session authentication
    headers = {'Cookie': 'Cookie=body:Language:english:id=-1'}
    auth_data = {'UserName': ont_username,
                 'PassWord': b64encode(ont_password.encode()),
                 'x.X_HW_Token': sid}
    r = s.post(ont_urlprefix + '/login.cgi', headers=headers,
               data=auth_data)
    return r.ok

def get_oi_iter(s):
    r = s.get(ont_urlprefix + '/html/amp/opticinfo/opticinfo.asp')
    if r.encoding is None:
        r.encoding = 'utf-8'
    return r.iter_lines(decode_unicode=True)


with requests.Session() as s, InfluxDBClient(host=influx_host, database=influx_db) as client:
    while True:
        for line in get_oi_iter(s):
            # The ONT doesn't report login failure in a programmatic way, we have to parse the content
            if 'Waiting...' in line:
                login(s)
                sleep(1)    # avoid DoSing if it really doesn't work
                break
            if line.startswith('var opticInfos ='):
                optdata = line[line.find('"') + 1:line.rfind('"')].split('","')
                oi = dict(zip(opticInfo, map(cleanval, optdata)))

                influx_data = [{
                    'measurement': 'OpticInfo',
                    'tags': {'VendorSN': oi['VendorSN']},
                    'fields': {k: v for k, v in oi.items() if k in wantedFields}
                    }]


                client.write_points(influx_data)
                sleep(interval)
                break

    # for a clean logout, but this does not happen
    #s.post(ont_urlprefix + '/logout.cgi?RequestFile=html/logout.html')
