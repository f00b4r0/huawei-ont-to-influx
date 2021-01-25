#!/usr/bin/env python3
import requests
import base64

# User vars
ont_host     = "192.168.100.1"
ont_username = "root"
ont_password = "adminHW"

# Build URL prefix
ont_urlprefix = "http://" + ont_host

# Start http session
ont_session = requests.Session()
# Get the mystery random stuff
req = ont_session.post(ont_urlprefix + "/asp/GetRandCount.asp")
sid = req.text[-32:]
# Session authentication
headers = {"Cookie": "Cookie=body:Language:english:id=-1"}
auth_data = {"UserName": ont_username, "PassWord": base64.b64encode(ont_password.encode()), "x.X_HW_Token": sid}
req = ont_session.post(ont_urlprefix + "/login.cgi", headers=headers, data=auth_data)
# Get optic info
req = ont_session.get(ont_urlprefix + "/html/amp/opticinfo/opticinfo.asp")
# Logout
ont_session.post(ont_urlprefix + "/logout.cgi?RequestFile=html/logout.html")

# Result parsing
for line in req.text.split("\n"):
  if line.startswith('var opticInfos'):
    opticInfos_split = line.split("\",\"")
    print("TxPower: {:s}".format(opticInfos_split[1]))
    print("RxPower: {:s}".format(opticInfos_split[2]))
    print("Voltage: {:s}".format(opticInfos_split[3]))
    print("Temperature: {:s}".format(opticInfos_split[4]))
    print("BiasCurrent: {:s}".format(opticInfos_split[5]))
    break

exit(0)
