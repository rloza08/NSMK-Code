#!/usr/bin/env python3
import os
import json
from utils.auto_logger import logger, runlogs_logger
import global_vars as gv
from utils.auto_utils import create_org_data_dir
import utils.auto_utils as utils
from utils.auto_pmdb import settings, load_cli_settings

CONFIG_DIR = "../../config"
RUNTIME_DIR = "../runtime"
TEMPLATES_DIR = "../../templates"

def make_pretty(my_json):
    return json.dumps(my_json, indent=4, sort_keys=False)

def json_writer(fpath, data):
    str = make_pretty(data)
    try:
        with open(fpath, 'w') as f:
            f.write(str)
    except Exception as err:
        logger.error("failure")
        runlogs_logger.error("failure")
        gv.fake_assert()

def json_reader(fpath):
    data = None
    cwd = os.getcwd()
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
    except Exception as err:
        logger.error("cwd {} fpath {}".format(cwd, fpath))
        runlogs_logger.error("cwd {} fpath {}".format(cwd, fpath))
        gv.fake_assert()

    return data

def get_orgid(org_name):
    config = json_reader("{}/safeway-config.json".format(CONFIG_DIR))
    networks = config[0]["network"]
    org_id=None
    for network in networks:
        if network["org_name"] == org_name:
            org_id=network["org_id"]
            break
    return org_id

def select_org(_org_name):
    settings["org-name"] = _org_name

def select_store(_store_name):
    settings["store-name"]= _store_name

## cli settings
def set_cli_selections(field=None, value=None):
    if field:
        settings["CLI"][field] = value
    json_writer("{}/cli-selections.json".format(RUNTIME_DIR), settings["CLI"])


def set_settings(field=None, value=None):
    assert(0)
    if field:
        settings[field] = value
    json_writer("{}/cli-selections.json".format(RUNTIME_DIR), settings)


def load_org(_orchestration_agent=None, org_name=None):
    settings["agent"] = _orchestration_agent
    settings["org-name"] = org_name
    settings["org-id"] = get_orgid(org_name)
    settings["org-data-dir"] = create_org_data_dir(settings["agent"])
    settings["store-name"] = None
    settings["store-number"] = None
    settings["time-stamp"] = None
    settings["netid"] = None
    #set_cli_selections()

def load_store_serials(store_name, serials_list):
    settings["serial1"] = None
    settings["serial2"] = None
    settings["device-name1"] = None
    settings["device-name2"] = None
    settings["serial"] = None
    settings["device-name"] = None

    serial_count = 0
    for item in serials_list:
        if store_name == item["Network name"]:
            if settings["serial1"]:
                settings["serial2"] = item["Serial"]
                settings["device-name2"] = item["Name"]
                serial_count +=1
            else:
                settings["serial1"] = item["Serial"]
                settings["device-name1"] = item["Name"]
                serial_count +=1
        if serial_count > 2:
            logger.error("store {} has too many serial".format(store_name))
            runlogs_logger.error("store {} has too many serial".format(store_name))
            gv.fake_assert()
            return 0
    return serial_count                


def load_store(_orchestration_agent, store_name):
    org_name = settings["org-name"]
    load_org(_orchestration_agent, org_name)
    store_name = "{}".format(store_name)
    settings["store-name"] = store_name
    store_number = utils.obtain_store_number(store_name)
    settings["store-number"] = store_number
    settings["time-stamp"] = utils.create_store_data_dir(_orchestration_agent)
    settings["netid"] = utils.obtain_netid(store_number, store_name)
    if not settings["netid"]:
        logger.error("store '{}' not found in org: {}".format(settings["store-name"], settings["org-name"]))
        runlogs_logger.error("store '{}' not found in org: {}".format(settings["store-name"], settings["org-name"]))
        runlogs_logger.error("store '{}' not found in org: {}".format(settings["store-name,"], settings["org-name"]))
        gv.fake_assert()
        return False
    # men_and_mice.get_vlan_funnel()
    set_cli_selections()
    return True

def load_empty_store(_orchestration_agent, store_name):
    org_name = settings["org-name"]
    load_org(_orchestration_agent, org_name)
    store_name = "{}".format(store_name)
    settings["store-name"] = store_name
    store_number = utils.obtain_store_number(store_name)
    settings["store-number"] = store_number
    settings["time-stamp"] = utils.create_store_data_dir(_orchestration_agent)
    # men_and_mice.get_vlan_funnel()
    set_cli_selections()
    return True

