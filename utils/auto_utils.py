#!/usr/bin/env python3
import re
import os
import utils.auto_globals as auto_globals
import datetime
import shutil
import pathlib
import utils.auto_logger as l
import sys
import  global_vars as gv

# Not really to be called from anywhere
# to get the store number simply call auto_globals.storeName, storeNumber, netid, orgid, org_name

def goahead_confirm(module):
    time.sleep(1)
    sys.stdout.flush()

    resp = input("\n# WARNING !!! #\n# Please review settings above for {} #\n\nType in 'yes' to proceed or any other character to abort."
                 "enter (yes/No):".format(module))

    if resp.lower() != "yes":
        l.runlogs_logger.error("Aborted by user !!!")
        l.runlogs_logger.error("Aborted by user !!!")
        gv.EOM()
        gv.fake_assert()

    print("Proceeding with {} deploy.".format(module))
    sys.stdout.flush()
    return True

def show_orglist(org_list):
    str = "deploying on the following org:"
    number = 0
    for org in org_list:
        number +=1
        str +=("\n\t\t{} - {}".format(number, org["org_name"]))
    l.runlogs_logger.info("{}".format(str))


def show_store_list(store_list):
    str = "deploying on the following stores:"
    number = 0
    for store in store_list:
        number +=1
        str +=("\n\t\t{} - {}".format(number, store["name"]))
    l.runlogs_logger.info("{}".format(str))

def show_selected_l3fwrules(l3fwrules):
    str = "deploying using {}:".format(l3fwrules)
    l.runlogs_logger.info("{}".format(str))

def show_selected_s2svpnrules(s2svpnrules):
    str = "deploying using {}:".format(s2svpnrules)
    l.runlogs_logger.info("{}".format(str))


def create_store_data_dir(orchestration_agent, minimum=False):
    org_name = auto_globals.org_name
    org_name = org_name.strip()
    aux = org_name.split()
    org_name = "".join(aux)
    store_number = auto_globals.store_number
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    auto_globals.folder_time_stamp = "../data/{}/{}/{}/{}/runtime".format(orchestration_agent, org_name, store_number, now)
    pathlib.Path(auto_globals.folder_time_stamp).mkdir(parents=True, exist_ok=True)

    if minimum is False:
        src = "../runtime/vlans_funnel.csv"
        shutil.copy(src, auto_globals.folder_time_stamp)
        src = "../runtime/in_use_dryrun.json"
        shutil.copy(src, auto_globals.folder_time_stamp)
        src = "../templates"
        shutil.copytree(src, auto_globals.folder_time_stamp+"/templates_used")
    return now

def create_org_data_dir(orchestration_agent):
    org_name = auto_globals.org_name
    org_name = org_name.strip()
    aux = org_name.split()
    org_name = "".join(aux)
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    # Windows does not like ":"
    if os.name == 'nt':
        now = "{}".format(now)
        now = now.replace(":", "_")

    auto_globals.folder_time_stamp = "../data/{}/{}/{}".format(orchestration_agent, org_name, now)
    pathlib.Path(auto_globals.folder_time_stamp).mkdir(parents=True, exist_ok=True)
    return now


def obtain_store_number(store_name):
    auto_globals.store_name = store_name
    store_number = re.sub("[^0-9]", "", store_name)
    store_number = store_number.zfill(4)
    auto_globals.store_number = store_number
    return store_number

def obtain_netid(storeNumber, storeName):
    import api.network as network
    netid = network.get_store_netid(storeName)
    auto_globals.netid=netid
    auto_globals.storeNumber = storeNumber
    return netid

def get_store_path(fname, path, extension):
    cwd = os.getcwd()
    org_name = auto_globals.org_name
    org_name = org_name.split(" ")
    org_name = "".join(org_name)
    if path=="data":
        now = auto_globals.time_stamp
        now = "{}".format(now)
        now = now.replace(":", "_")
        fName = "{}/../{}/{}/{}/{}/{}/runtime/{}.{}".format(cwd, path, auto_globals.orchestration_agent, org_name, auto_globals.store_number, now, fname, extension)
    else:
        fName = "{}/../{}/{}.{}".format(cwd, path, fname, extension)
    return fName

def get_org_path(fname, path, extension):
    fName = "{}/{}.{}".format(auto_globals.folder_time_stamp, fname, extension)
    return fName

def get_path(fname, path, extension):
    if path == "ORG":
        fname = get_org_path(fname, path, extension)
    else:
        fname = get_store_path(fname, path, extension)
    return fname


def get_key_value_in_data(json_data, keyField, valueField, match):
    dictList = json_data
    value = None
    success = False
    for dictItem in dictList:
        if dictItem[keyField] == match:
            value = dictItem[valueField]
            success = True
            break
    return success, value

def get_key_value(fname, keyField, valueField, match):
    json_data = open(fname).read()
    success, value = get_key_value_in_data(json_data, keyField, valueField, match)
    return success, value

if __name__ == '__main__':
    # auto_globals.setStoreName(store_name = "SHAWS_9611", org_name = "API Testing ORG")
    auto_globals.storeName = " SHAWS_  7777 "
    auto_globals.storeNumber = int(re.sub("[^0-9]", "", auto_globals.storeName))
    auto_globals.org_name = "   API Testing ORG2 "

    create_store_data_dir()

import time
str= time.strftime("%H:%M:%S")
