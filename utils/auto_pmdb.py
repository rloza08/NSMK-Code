#!/usr/bin/env python3
import json
# from utils.auto_logger import logger, runlogs_logger
import global_vars as gv
import os

settings = {}

RUNTIME_DIR = "../runtime"
CONFIG_DIR = "../../config"
TEMPLATES_DIR = "../../templates"

def json_reader(fpath):
    data = None
    cwd = os.getcwd()
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
    except Exception as err:
        # logger.error("cwd {} fpath {}".format(cwd, fpath))
        # runlogs_logger.error("cwd {} fpath {}".format(cwd, fpath))
        gv.fake_assert()

    return data


def load_cli_settings():
    global settings
    settings["CLI"] = json_reader("{}/cli-selections.json".format(RUNTIME_DIR))


init_pmdb_flag = False

from copy import deepcopy
def pmdb_init():
    global init_pmdb_flag
    global settings
    load_cli_settings()
    settings["org-name"] = None
    settings["store-name"]= None
    settings["agent"] = None
    settings["org-id"] = None
    settings["folder-time-stamp"] = None
    settings["store-name"] = None
    settings["store-number"] = None
    settings["time-stamp"] = None
    settings["netid"] = None
    settings["device-name"] = None
    settings["vlans-add-list"] = None

    fname = settings["CLI"].get("vlans-add-list")
    if fname:
        aux = json_reader("{}/{}.json".format(TEMPLATES_DIR, fname))
        settings["vlans-add-list"] = aux

    fname = settings["CLI"].get("vlans-delete-list")
    if settings["CLI"].get("vlans-delete-list"):
        aux = json_reader("{}/{}.json".format(TEMPLATES_DIR, fname))
        settings["vlans-delete-list"] = aux


    fname = settings["CLI"].get("networks-serials")
    if fname:
        aux = json_reader("{}/{}.json".format(TEMPLATES_DIR, fname))
        settings["networks-serials"] = aux
    else:
        print("networks-serials {}  not found".format(fname))


    config = json_reader("../../config/safeway-config.json")
    settings["CONFIG"] = dict()
    settings["CONFIG"]["network"] = config[0]["network"]
    firewall=config[0]["firewall"]
    settings["CONFIG"]["static-route-next-hop"] = firewall['static_route_next_hop']
    vlan=config[0]["vlan"]
    settings["CONFIG"]["funnel-file"]=vlan["funnel_file"]
    settings["CONFIG"]["netx-file"]=vlan['netx_file']
    settings["CONFIG"]["device-prefix"] = vlan["device_prefix"]
    settings["CONFIG"]["device-postfix"] = vlan["device_postfix"]
    vpn = config[0]["vpn"]
    settings["CONFIG"]["hubnetworks"] = vpn["hubnetworks"]
    settings["CONFIG"]["defaultroute"] = vpn["defaultroute"]

    # Netx and Non-Netx
    if gv.USE_NON_NETX:
        settings["NON-NETX"] = dict()
        fname = "vlans-non-netx"
        non_netx_stores = json_reader("{}/{}.json".format(TEMPLATES_DIR, fname))
        nn_map = {}
        # Builds list of subnets per store
        for entry in non_netx_stores:
            store_number = entry["Store"]
            if nn_map.get(store_number) is None:
                nn_map[store_number] = []
            nn_map[store_number].append(deepcopy(entry))
        settings["NON-NETX"] = nn_map

    init_pmdb_flag = True

