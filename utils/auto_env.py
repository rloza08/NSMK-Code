#!/usr/bin/env python3
import utils.auto_globals as auto_globals
import utils.auto_logger as l
from utils.auto_globals import CONFIG_DIR, vlans_add_list
from utils.auto_config import json_reader, make_pretty
from copy import deepcopy
from utils._json import Json
import shutil
import os
from utils.auto_csv import convert_to_json

def add_entry_to_template(t_new, vlan):
    vlan_id = int(vlan['Vlan'])
    o4 = vlan['Subnet'].split('.')
    o4 = o4[3]
    o4 = o4.split("/")
    o4 = int(o4[0])
    entry = {}
    entry["id"] = vlan_id
    entry["networkId"] =  "{{networkid}}"
    entry["name"] =  vlan['Description']
    entry["applianceIp"] =  "{{{{vlan[{}]['octets']}}}}.{}".format(vlan_id, o4+1)
    entry["subnet"] =  "{{{{vlan[{}]['subnet']}}}}".format(vlan_id)
    entry["dnsNameservers"] =  "upstream_dns"
    entry["fixedIpAssignments"] =  {}
    entry["reservedIpRanges"] =  []
    t_new.append(entry)



def update_vlan_template(funnel_file="vlans_funnel",
                         vlans_template_file="jinja_vlans_template",
                         vlans_template_file_previous="jinja_vlans_template_previous",
                         vlans_template_file_new = "jinja_vlans_template") :

    vlans_new = json_reader("{}/{}.json".format(CONFIG_DIR, funnel_file))
    vlans_template_orig = json_reader("{}/{}.json".format(CONFIG_DIR, vlans_template_file))

    t_old = vlans_template_orig
    t_new = deepcopy(t_old)

    for funnel_vlan in vlans_new:
        found = False
        vlan = int(funnel_vlan['Vlan'])
        # Check with Jas
        if vlan == 1:
            continue
        for item in t_new:
            if int(vlan) == item["id"]:
                found = True
                break

        if not found:
            add_entry_to_template(t_new, funnel_vlan)

    #vlans_new = json_writer(funnel_new_file)
    # create a backup for the existing jinja template
    cwd = os.getcwd()
    src = "{}/{}.json".format(CONFIG_DIR, vlans_template_file)
    dst = "{}/{}.json".format(CONFIG_DIR, vlans_template_file_previous)
    destination = open(dst, 'wb')
    shutil.copyfileobj(open(src, 'rb'), destination)

    Json.writer(vlans_template_file_new, t_new, path="config")

    tpl = make_pretty(t_new)
    print (tpl)
    return t_new

def copy_and_patch_funnel():
    try:
        cwd = os.getcwd()
        patch = "{}/../../config/vlans_funnel.patch.csv".format(cwd)
        src = "{}/../menAndMice/funnel.csv".format(cwd)
        dst = "{}/../../config/vlans_funnel.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        shutil.copyfileobj(open(patch, 'rb'), destination)
        destination.close()
        convert_to_json("vlans_funnel", "config",None)
    except:
        l.logger.error("failed")
        assert (0)


def ENTER_ENV_VLANS(agent):
    if agent != "cli-deploy-vlans-add":
        copy_and_patch_funnel()
        org_group = auto_globals.networks_org
        store_list = auto_globals.networks_store_list
        return org_group, store_list

    cwd = os.getcwd()
    try:

        # Backup the funnel file
        src = "{}/../../config/vlans_funnel.csv".format(cwd)
        dst = "{}/../../config/vlans_funnel_orig.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        destination.close()

        src = "{}/../menAndMice/funnel.csv".format(cwd)
        dst = "{}/../../config/vlans_funnel.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)

        # 99x Vlan patch that is always used
        patch_01 = "{}/../../config/vlans_funnel.patch.csv".format(cwd)
        shutil.copyfileobj(open(patch_01, 'rb'), destination)

        # Vlan patch just for this run
        patch_02 = "{}/../../templates/{}.csv".format(cwd, vlans_add_list)
        shutil.copyfileobj(open(patch_02, 'rb'), destination)
        destination.close()
        convert_to_json("vlans_funnel", "config",None)
    except:
        l.logger.error("failed")
        assert (0)


    src = "{}/../../config/jinja_vlans_template.json".format(cwd)
    dst = "{}/../../config/jinja_vlans_template_orig.json".format(cwd)
    destination = open(dst, 'wb')
    shutil.copyfileobj(open(src, 'rb'), destination)
    destination.close()


    update_vlan_template(funnel_file="vlans_funnel",
                             vlans_template_file="jinja_vlans_template",
                             vlans_template_file_previous="jinja_vlans_template_previous",
                             vlans_template_file_new="jinja_vlans_template")

    org_group = auto_globals.vlans_org
    store_list = auto_globals.vlans_store_list
    return org_group, store_list



def LEAVE_ENV_VLANS(agent):
    if agent != "cli-deploy-vlans-add":
        return

    # Now restore the men and mice file in config back to
    # its original state
    cwd = os.getcwd()
    try:
        src = "{}/../../config/jinja_vlans_template_orig.json".format(cwd)
        dst = "{}/../../config/jinja_vlans_template.json".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        destination.close()

        src = "{}/../../config/vlans_funnel_orig.csv".format(cwd)
        dst = "{}/../../config/vlans_funnel.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        destination.close()
    except:
        l.logger.error("failed")
        assert (0)


if __name__ == '__main__':
    pass
