#!/usr/bin/env python3
import re
import os
import datetime
import shutil
import pathlib
import utils.auto_logger as l
import sys
import utils.auto_pmdb as pmbd
import  global_vars as gv
import time
from utils.auto_pmdb import settings, pmdb_init

# Not really to be called from anywhere
# to get the store number simply call auto_globals.storeName, storeNumber, netid, orgid, org_name
TABS=3*"\t"

def is_numeric(s):
    try:
        int(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def is_non_zero_number(s):
    if is_numeric(s) == False:
        return False
    if int(s) == 0 :
        return False
    return True


def is_numeric_in_range(number, lo, hi):
    try:
        if is_numeric(number):
            if int(number) >= lo and int(number) <= hi:
                return True
    except:
        str = "invalid range for {} : lo: {} hi: {}".format(number, lo, hi)
        # l.message_user(str)
    return False

def goahead_confirm(_module):
    time.sleep(1)
    sys.stdout.flush()

    if gv.force_yes is False:
        resp = input("\n# WARNING !!! #\n# Please review settings above for {} #\n\nType in 'yes' to proceed or any other character to abort."
                     "enter (yes/No):".format(_module))

        if resp.lower() != "yes":
            l.runlogs_logger.error("Aborted by user !!!")
            gv.EOM()
            gv.fake_abort()
            print("Proceeding with {} deploy.".format(_module))
    sys.stdout.flush()
    return True

def show_orglist(org_list):
    str = "deploying on the following org:"
    number = 0
    for org in org_list:
        number +=1
        str +=("\n{} - {}".format(number, org["org_name"]))
    l.logger.info("{}\n".format(str))
    l.runlogs_logger.info("{}\n".format(str))

def show_store_list(store_list):
    str = "deploying on the following stores:"
    number = 0
    for store in store_list:
        number +=1
        str +=("\n{}{} - {}".format(TABS, number, store["name"]))
    l.logger.info("{}\n".format(str))
    l.runlogs_logger.info("{}\n".format(str))

def show_vlans_add_list():
    str = "adding the following vlans:"
    number = 0
    vlans_add_list = settings["vlans-add-list"]
    for vlan in vlans_add_list:
        number +=1
        str +=("\n{}{} - {} {} {}".format(TABS, number, vlan["Vlan"], vlan["Subnet"], vlan["Description"]))
    l.logger.info("{}\n".format(str))
    l.runlogs_logger.info("{}\n".format(str))

def show_vlans_delete_list(vlans_add_list):
    str = "delete the following vlans:"
    number = 0
    for vlan in vlans_add_list:
        number +=1
        str +=("\n{}{} - {}".format(TABS, number, vlan))
    l.logger.info("{}\n".format(str))
    l.runlogs_logger.info("{}\n".format(str))

def show_selected_l3fwrules(l3fwrules):
    str = "deploying using {}:".format(l3fwrules)
    l.runlogs_logger.info("{}".format(str))

def show_selected_s2svpnrules(s2svpnrules):
    str = "deploying using {}:".format(s2svpnrules)
    l.runlogs_logger.info("{}".format(str))

def create_store_data_dir(orchestration_agent):
    store_name = settings["store-name"]
    success, _, _, _ = is_valid_store_name(store_name)
    if not success:
        return None
    org_name = settings["org-name"]
    org_name = org_name.strip()
    aux = org_name.split()
    org_name = "".join(aux)
    store_number = settings["store-number"]
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    settings["folder-time-stamp"] = "../../data/{}/{}/{}/{}".format(orchestration_agent, org_name, store_number, now)
    if orchestration_agent not in ["cli-deploy-s2svpnrules", "cli-get-s2svpnrules"]:
        pathlib.Path(settings["folder-time-stamp"]).mkdir(parents=True, exist_ok=True)
    return now

def create_org_data_dir(orchestration_agent):
    org_name = settings["org-name"]
    if org_name is None:
        return
    org_name = org_name.strip()
    aux = org_name.split()
    org_name = "".join(aux)
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    # Windows does not like ":"
    if os.name == 'nt':
        now = "{}".format(now)
        now = now.replace(":", "_")

    org_data_dir = "../../data/{}/{}/{}".format(orchestration_agent, org_name, now)
    if orchestration_agent in ["cli-deploy-s2svpnrules", "cli-get-s2svpnrules"]:
            pathlib.Path(org_data_dir).mkdir(parents=True, exist_ok=True)
    return org_data_dir

def obtain_store_number(store_name):
    if not is_valid_store_name(store_name):
        return None
    settings["store-name"] = store_name
    store_number = re.sub("[^0-9]", "", store_name)
    store_number = store_number.zfill(4)
    settings["store-number"] = store_number
    return store_number

def obtain_netid(storeNumber, storeName):
    import api.network as network
    netid = network.get_store_netid(storeName)
    settings["netid"]=netid
    settings["storeNumber"] = storeNumber
    return netid

def get_store_path(fname, path, extension):
    cwd = os.getcwd()
    if path=="data":
        org_name = settings["org-name"]
        org_name = org_name.split(" ")
        org_name = "".join(org_name)
        now = settings["time-stamp"]
        now = "{}".format(now)
        now = now.replace(":", "_")
        fName = "{}/../../{}/{}/{}/{}/{}/{}.{}".format(cwd, path, settings["agent"], org_name, settings["store-number"], now,
                                                               fname, extension)
    elif path == "templates":
        fName = "{}/../../{}/{}.{}".format(cwd, path, fname, extension)
    elif path == "config":
        fName = "{}/../../{}/{}.{}".format(cwd, path, fname, extension)
    elif path == "runtime":
        fName = "{}/../{}/{}.{}".format(cwd, path, fname, extension)
    else:
        fName = "{}/{}/{}.{}".format(cwd, path, fname, extension)
    return fName

def get_org_path(fname, path, extension):
    cwd = os.getcwd()
    org_data_dir = settings["org-data-dir"]
    fName = "{}/{}/{}.{}".format(cwd, org_data_dir, fname, extension)
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

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

"""
    Store name is in the format 
    XXX_NNNN
    where XXX is upper-case (A-Z)
          NNNN is numeric (0000-9999)
"""

def is_valid_store_group(group):
    if group is None:
        return False
    if len(group) != 3:
        return False

    group_c = list(group)
    for c in group_c:
        if c in char_range('A', 'Z'):
            pass
        else:
            return False
    return True


def is_valid_store_name(name):
    if len(name) != 8 and len(name) !=4:
        return False, None, None, None

    if len(name) == 8:
        aux = name.split("_")
        group = aux[0]

        if is_valid_store_group(group) is False:
            return False, None, None, None

        if len(aux) != 2 :
            return False, None, None, None
        store_number = aux[1]
    else:
        store_number = name
        group = "NOGROUP"
    if is_numeric_in_range(store_number, 1, 9999)==False:
        return False, None, None, None
    return True, name, group, store_number

# Meraki serial
# eg. "Q2PN-XXNJ-H2FA",
def is_valid_serial_number(serial):
    if len(serial) != 14:
        return False

    blocks = serial.split("-")
    if len(blocks) != 3:
        return False

    for block in blocks:
        if len(block) !=4:
            return False
    return True

if __name__ == '__main__':
    pmdb_init()
    print (settings)
    pass

