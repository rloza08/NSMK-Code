#!/usr/bin/env python3
import os
#import utils.auto_globals as auto_globals
import json
import traceback
import utils.auto_logger as l

l.setup()

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
        traceback.print_tb(err.__traceback__)
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

def get_clone_id(orgid):
    networks = config[0]["network"]
    for network in networks:
        if orgid == network["org_id"]:
            clone_id = network['clone_id']
            return clone_id
    assert(0)

config = json_reader("../config/safeway-config.json")
#orgs = json_reader("../config/safeway-orgs.json")

# import utils.auto_utils as utils
# utils.get_key_value_in_data()
# success, value = utils.get_key_value_in_data(json_data=config["network"], keyField="org_name", valueField="org_id",
#                                              match=)

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
vlan_update_only=vlan["update_only"]
netx_file=vlan['netx_file']
device_prefix = vlan["device_prefix"]
device_postfix = vlan["device_postfix"]

vpn = config[0]["vpn"]

hubnetworks=vpn["hubnetworks"]
defaultroute=vpn["defaultroute"]

logging_debug_level=config[0]["logging"]["debug_level"]