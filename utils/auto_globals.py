#!/usr/bin/env python3
import os
import json
import traceback
import utils.auto_logger as l



orchestration_agent, dryrun, store_name, store_number, org_name, orgid, netid = None, None, None, None, None, None, None
folder_time_stamp = None
time_stamp = None
deploy_clone_source = None
deploy_org = None
deploy_store_list = None
deploy_l3fwrules_version = None

l3fwrules_org = None
l3fwrules_store_list = None
l3fwrules_version = None
s2svpnrules_org = None
s2svpnrules_version = None
production = None


def make_pretty(my_json):
    return json.dumps(my_json, indent=4, sort_keys=True)

def json_writer(fpath, data):
    str = make_pretty(data)
    try:
        with open(fpath, 'w') as f:
            f.write(str)
    except Exception as err:
        l.logger.error("failure")
        traceback.print_tb(err.__traceback__)
        assert (0)

def json_reader(fpath):
    data = None
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
    except Exception as err:
        l.logger.error("fpath:{} {}".format(fpath))
        traceback.print_tb(err.__traceback__)
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
    json_writer("../tmp/in_use_org.json", item)


def select_store(_store_name):
    global store_name
    item = {}
    item["store_name"] = _store_name
    store_name = _store_name
    json_writer("../tmp/in_use_store.json", item)


## cli sets
def set_run_dry(dryrun=True):
    item = json_reader("../config/cli-selections.json")
    item["dryrun"] = dryrun
    json_writer("../config/cli-selections.json", item)

def set_deploy_org(deploy_org):
    item = json_reader("../config/cli-selections.json")
    item["deploy-org"] = deploy_org
    json_writer("../config/cli-selections.json", item)

def set_deploy_store_list(deploy_store_list):
    item = json_reader("../config/cli-selections.json")
    item["deploy-store-list"] = deploy_store_list
    json_writer("../config/cli-selections.json", item)


def set_l3fwrules_org(deploy_org):
    item = json_reader("../config/cli-selections.json")
    item["l3fwrules-org"] = deploy_org
    json_writer("../config/cli-selections.json", item)

def set_l3fwrules_store_list(store_list):
   item = json_reader("../config/cli-selections.json")
   item["l3fwrules-store-list"] = store_list
   json_writer("../config/cli-selections.json", item)

def set_deploy_l3fwrules_version(version):
    item = json_reader("../config/cli-selections.json")
    item["deploy-l3fwrules-version"] = version
    json_writer("../config/cli-selections.json", item)

def set_l3fwrules_version(version):
    item = json_reader("../config/cli-selections.json")
    item["l3fwrules-version"] = version
    json_writer("../config/cli-selections.json", item)

def set_s2svpnrules_org(org):
    item = json_reader("../config/cli-selections.json")
    item["s2svpnrules-org"] = org
    json_writer("../config/cli-selections.json", item)

def set_s2svpnrules_version(version):
    item = json_reader("../config/cli-selections.json")
    item["s2svpnrules-version"] = version
    json_writer("../config/cli-selections.json", item)

def set_clone_source(source):
    item = json_reader("../config/cli-selections.json")
    item["deploy-clone-source"] = source
    json_writer("../config/cli-selections.json", item)

def set_production(mode):
    item = json_reader("../config/cli-selections.json")
    item["production"] = mode
    json_writer("../config/cli-selections.json", item)

def get_settings():
    global dryrun, store_name, org_name, log_verbose
    item = json_reader("../tmp/in_use_store.json")
    store_name = item.get("store_name")
    item = json_reader("../tmp/in_use_org.json")
    org_name = item.get("org_name")
    item = json_reader("../config/in_use_dryrun.json")
    dryrun = item.get("dryrun", True)
    return dryrun, store_name, org_name

def get_cli_settings():
    global deploy_clone_source, deploy_org, deploy_store_list
    global deploy_l3fwrules_version, l3fwrules_org, l3fwrules_store_list
    global l3fwrules_version, s2svpnrules_org
    global s2svpnrules_org, s2svpnrules_version
    global production

    item = json_reader("../config/cli-selections.json")
    result = make_pretty(item)
    deploy_clone_source = item.get("deploy-clone-source")
    deploy_org = item.get("deploy-org")
    deploy_store_list = item.get("deploy-store-list")
    deploy_l3fwrules_version = item.get("deploy-l3fwrules-version")

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
    assert(store_name)
    assert(org_name)

    orgid = get_orgid(org_name)   # TODO load by an API CALL
    assert(orgid)

    import api.men_and_mice as men_and_mice
    men_and_mice.get_vlan_funnel()
    import utils.auto_utils as utils

    store_name = "{}".format(store_name)
    store_number= utils.obtain_store_number(store_name)
    time_stamp = utils.create_store_data_dir(orchestration_agent, minimum)
    folder_time_stamp = time_stamp
    netid = utils.obtain_netid(store_number, store_name)
    if not netid:
        l.logger.error("store '{}' not found in org: {}".format(store_name, org_name))
        l.firewall_logger.error("store '{}' not found in org: {}".format(store_name, org_name))
        l.vpn_firewall_logger.error("store '{}' not found in org: {}".format(store_name, org_name))
    assert(netid)


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
