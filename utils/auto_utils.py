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
import time

# Not really to be called from anywhere
# to get the store number simply call auto_globals.storeName, storeNumber, netid, orgid, org_name
TABS=6*"\t"

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
        str +=("\n{}{} - {}".format(number, org["org_name"]))
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

def show_vlans_add_list(vlans_add_list):
    str = "adding the following vlans:"
    number = 0
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


def create_store_data_dir(orchestration_agent, minimum=False):
    org_name = auto_globals.org_name
    org_name = org_name.strip()
    aux = org_name.split()
    org_name = "".join(aux)
    store_number = auto_globals.store_number
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    auto_globals.folder_time_stamp = "../../data/{}/{}/{}/{}/runtime".format(orchestration_agent, org_name, store_number, now)
    pathlib.Path(auto_globals.folder_time_stamp).mkdir(parents=True, exist_ok=True)

    if minimum is False:
        src = "../config/vlans_funnel.csv"
        shutil.copy(src, auto_globals.folder_time_stamp)
        src = "../../templates"
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

    auto_globals.folder_time_stamp = "../../data/{}/{}/{}".format(orchestration_agent, org_name, now)
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
        fName = "{}/../../{}/{}/{}/{}/{}/runtime/{}.{}".format(cwd, path, auto_globals.orchestration_agent, org_name, auto_globals.store_number, now, fname, extension)
    elif path == "templates":
        fName = "{}/../../{}/{}.{}".format(cwd, path, fname, extension)
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
        return False, None, None

    if len(name) == 8:
        aux = name.split("_")
        group = aux[0]

        if is_valid_store_group(group) is False:
            return False, None, None

        if len(aux) != 2 :
            return False, None, None
        store_number = aux[1]
    else:
        store_number = int(name)
        group = ""
    if is_numeric_in_range(store_number, 1, 9999)==False:
        return False, None, None
    return True, group, store_number

if __name__ == '__main__':
    # auto_globals.setStoreName(store_name = "SHAWS_9611", org_name = "API Testing ORG")
#     auto_globals.storeName = " SHAWS_  7777 "
#     auto_globals.storeNumber = int(re.sub("[^0-9]", "", auto_globals.storeName))
#     auto_globals.org_name = "   API Testing ORG2 "
#
#     create_store_data_dir()
#
# import time
# str= time.strftime("%H:%M:%S")

    name = "SHA_0113"
    valid, group, store_number = is_valid_store_name(name)
    print ("valid: {} name: {} group :{} store_number: {}".format(valid, name, group, store_number))
