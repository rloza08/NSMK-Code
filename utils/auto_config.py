#!/usr/bin/env python3
import os
import json
import traceback
import utils.auto_logger as l
import global_vars as gv

l.setup()

global clone_id
clone_id = None

def make_pretty(my_json):
    return (json.dumps(my_json, indent=4, sort_keys=False))

def json_reader(fpath):
    data = None
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
        str = make_pretty(data)
        l.logger.debug("auto_utils.json_reader:\n{}".format(str))
    except Exception as err:
        l.logger.error("fpath:{} {}".format(fpath))
        l.runlogs_logger.error("fpath:{} {}".format(fpath))
        gv.fake_assert()
    return data

def setup_proxy():
    user = os.environ.get("PROXY_USER", None)
    password = os.environ.get("PROXY_PWD", None)
    if not user and not password:
        return
    if user and password:
        url = "http://{}:{}@phxproxyvip.safeway.com:8080".format(user, password)
    else:
        url = "http://culproxyvip.safeway.com:8080"
    os.environ['HTTPS_PROXY'] = url

def set_clone_id(id):
    global clone_id
    clone_id = id

def get_clone_id():
    global clone_id
    return clone_id

config = json_reader("../config/safeway-config.json")

api_key = os.environ.get("API_KEY", None)
assert(api_key)
network=config[0]["network"]

firewall=config[0]["firewall"]
static_route_next_hop=firewall['static_route_next_hop']

dryrun = config[0]["dryrun"]
dryrun_netx_fake_ip=dryrun["netx_fake_ip"]

setup_proxy()

vlan=config[0]["vlan"]
vlan_funnel_file=vlan["funnel_file"]
netx_file=vlan['netx_file']
device_prefix = vlan["device_prefix"]
device_postfix = vlan["device_postfix"]

vpn = config[0]["vpn"]

hubnetworks=vpn["hubnetworks"]
defaultroute=vpn["defaultroute"]

