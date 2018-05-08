#!/usr/bin/env python3
import os
import json
import utils.auto_logger as l
import global_vars as gv


CONFIG_DIR = "../../config"

orchestration_agent, dryrun, store_name, store_number, org_name, orgid, netid = None, None, None, None, None, None, None
folder_time_stamp = None
time_stamp = None
networks_clone_source = None
networks_org = None
networks_store_list = None
site_org = None
site_store_list = None
site_l3fwrules_version = None

l3fwrules_org = None
l3fwrules_store_list = None
l3fwrules_version = None
s2svpnrules_org = None
s2svpnrules_version = None
production = None

vlans_add_org = None
vlans_add_store_list = None
vlans_add_list = None

vlans_delete_org = None
vlans_delete_store_list = None
vlans_delete_list = None

def make_pretty(my_json):
    return json.dumps(my_json, indent=4, sort_keys=False)

def json_writer(fpath, data):
    str = make_pretty(data)
    try:
        with open(fpath, 'w') as f:
            f.write(str)
    except Exception as err:
        l.logger.error("failure")
        l.runlogs_logger.error("failure")
        gv.fake_assert()

def json_reader(fpath):
    data = None
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
    except Exception as err:
        l.logger.error("fpath:{} {}".format(fpath))
        l.runlogs_logger.error("fpath:{} {}".format(fpath))
        gv.fake_assert()

    return data

def _get_orgid(org_name):
    orgs = json_reader("../config/safeway-orgs.json")
    orgid=None
    for org in orgs:
        if org["name"] == org_name:
            orgid=org["id"]
            break
    return orgid

def get_orgid(org_name):
    config = json_reader("../config/safeway-config.json")
    networks = config[0]["network"]
    orgid=None
    for network in networks:
        if network["org_name"] == org_name:
            orgid=network["org_id"]
            break
    return orgid

def select_org(org_name):
    item = {}
    item["org_name"]=org_name.strip()
    json_writer("../runtime/in_use_org.json", item)


def select_store(_store_name):
    global store_name
    item = {}
    item["store_name"] = _store_name
    store_name = _store_name
    json_writer("../runtime/in_use_store.json", item)


## cli sets
def set_run_dry(dryrun=True):
    item = json_reader("../../config/in_use_dryrun")
    item["dryrun"] = dryrun
    json_writer("../../config/in_use_dryrun", item)


def set_vlans_add_org(_vlans_add_org):
    global vlans_add_org
    vlans_add_org = _vlans_add_org
    item = json_reader("../runtime/cli-selections.json")
    item["vlans-add-org"] = vlans_add_org
    json_writer("../runtime/cli-selections.json", item)

def set_vlans_add_store_list(_vlans_store_list):
    global vlans_add_store_list
    vlans_add_store_list = _vlans_store_list
    item = json_reader("../runtime/cli-selections.json")
    item["vlans-add-store-list"] = vlans_add_store_list
    json_writer("../runtime/cli-selections.json", item)

def set_vlans_add_list(_vlans_add_list):
    global vlans_add_list
    vlans_add_list = _vlans_add_list
    item = json_reader("../runtime/cli-selections.json")
    item["vlans-add-list"] = vlans_add_list
    json_writer("../runtime/cli-selections.json", item)

#-----------------------------------------------------------
def set_vlans_delete_org(_vlans_delete_org):
    global vlans_delete_org
    vlans_delete_org = _vlans_delete_org
    item = json_reader("../runtime/cli-selections.json")
    item["vlans-delete-org"] = vlans_delete_org
    json_writer("../runtime/cli-selections.json", item)

def set_vlans_delete_store_list(_vlans_delete_store_list):
    global vlans_delete_store_list
    vlans_delete_store_list = _vlans_delete_store_list
    item = json_reader("../runtime/cli-selections.json")
    item["vlans-delete-store-list"] = vlans_delete_store_list
    json_writer("../runtime/cli-selections.json", item)

def set_vlans_delete_list(_vlans_delete_list):
    global vlans_add_list
    vlans_delete_list = _vlans_delete_list
    item = json_reader("../runtime/cli-selections.json")
    item["vlans-delete-list"] = vlans_delete_list
    json_writer("../runtime/cli-selections.json", item)


def set_networks_org(networks_org):
    item = json_reader("../runtime/cli-selections.json")
    item["networks-org"] = networks_org
    item["site-org"] = networks_org
    json_writer("../runtime/cli-selections.json", item)

def set_networks_store_list(networks_store_list):
    item = json_reader("../runtime/cli-selections.json")
    item["networks-store-list"] = networks_store_list
    item["site-store-list"] = networks_store_list
    json_writer("../runtime/cli-selections.json", item)


def set_l3fwrules_org(param):
    item = json_reader("../runtime/cli-selections.json")
    item["l3fwrules-org"] = param
    json_writer("../runtime/cli-selections.json", item)

def set_l3fwrules_store_list(store_list):
   item = json_reader("../runtime/cli-selections.json")
   item["l3fwrules-store-list"] = store_list
   json_writer("../runtime/cli-selections.json", item)

def set_site_l3fwrules_version(version):
    item = json_reader("../runtime/cli-selections.json")
    item["site-l3fwrules-version"] = version
    json_writer("../runtime/cli-selections.json", item)

def set_l3fwrules_version(version):
    item = json_reader("../runtime/cli-selections.json")
    item["l3fwrules-version"] = version
    json_writer("../runtime/cli-selections.json", item)

def set_s2svpnrules_org(org):
    item = json_reader("../runtime/cli-selections.json")
    item["s2svpnrules-org"] = org
    json_writer("../runtime/cli-selections.json", item)

def set_s2svpnrules_version(version):
    item = json_reader("../runtime/cli-selections.json")
    item["s2svpnrules-version"] = version
    json_writer("../runtime/cli-selections.json", item)

def set_clone_source(source):
    item = json_reader("../runtime/cli-selections.json")
    item["networks-clone-source"] = source
    json_writer("../runtime/cli-selections.json", item)

def set_production(mode):
    item = json_reader("../runtime/cli-selections.json")
    item["production"] = mode
    json_writer("../runtime/cli-selections.json", item)

def get_settings():
    global dryrun, store_name, org_name, log_verbose
    item = json_reader("../runtime/in_use_store.json")
    store_name = item.get("store_name")
    item = json_reader("../runtime/in_use_org.json")
    org_name = item.get("org_name")
    item = json_reader("../config/in_use_dryrun.json")
    dryrun = item.get("dryrun", True)
    return dryrun, store_name, org_name

def get_cli_settings():
    global networks_clone_source, networks_org, networks_store_list
    global site_l3fwrules_version, l3fwrules_org, l3fwrules_store_list
    global vlans_add_org, vlans_add_store_list, vlans_add_list
    global vlans_delete_org, vlans_delete_store_list, vlans_delete_list
    global l3fwrules_version, s2svpnrules_org
    global s2svpnrules_org, s2svpnrules_version
    global production

    item = json_reader("../runtime/cli-selections.json")
    result = make_pretty(item)
    networks_clone_source = item.get("networks-clone-source")
    networks_org = item.get("networks-org")
    networks_store_list = item.get("networks-store-list")
    site_l3fwrules_version = item.get("site-l3fwrules-version")

    vlans_add_org = item.get("vlans-add-org")
    vlans_add_store_list = item.get("vlans-add-store-list")
    vlans_add_list = item.get("vlans-add-list")

    vlans_delete_org = item.get("vlans-delete-org")
    vlans_delete_store_list = item.get("vlans-delete-store-list")
    vlans_delete_list = item.get("vlans-delete-list")


    l3fwrules_org = item.get("l3fwrules-org")
    l3fwrules_store_list = item.get("l3fwrules-store-list")
    l3fwrules_version = item.get("l3fwrules-version")
    s2svpnrules_org = item.get("s2svpnrules-org")
    s2svpnrules_version = item.get("s2svpnrules-version")
    production = item.get("production")
    return item

def load_store(_orchestration_agent, minimum=False):
    """
    Sets the store_name to be used
    Sets the orgId , which is looked up in /config/config-orgs.json
    Queries meraki and finds what is the netid for the store
    """
    global orchestration_agent, netid, store_number, store_name, org_name, orgid, time_stamp
    orchestration_agent = _orchestration_agent

    dryrun, store_name, org_name = get_settings()
    if store_name is None:
        return False
    if org_name is None:
        return False

    orgid = get_orgid(org_name)   # TODO load by an API CALL
    if orgid is None:
        return False

    # import api.men_and_mice as men_and_mice
    # men_and_mice.get_vlan_funnel()
    import utils.auto_utils as utils

    store_name = "{}".format(store_name)
    store_number= utils.obtain_store_number(store_name)
    time_stamp = utils.create_store_data_dir(orchestration_agent, minimum)
    netid = utils.obtain_netid(store_number, store_name)
    if not netid:
        l.logger.error("store '{}' not found in org: {}".format(store_name, org_name))
        l.runlogs_logger.error("store '{}' not found in org: {}".format(store_name, org_name))
        l.runlogs_logger.error("store '{}' not found in org: {}".format(store_name, org_name))
        gv.fake_assert()
        return False
    return True


def load_org(_orchestration_agent):
    global orchestration_agent, folder_timer_stamp
    orchestration_agent = _orchestration_agent

    dryrun, store_name, org_name = get_settings()
    assert(org_name)

    orgid = get_orgid(org_name)   # TODO load by an API CALL
    assert(orgid)

    from utils.auto_utils import  create_org_data_dir
    folder_time_stamp = create_org_data_dir(orchestration_agent)


get_settings()
get_cli_settings()
