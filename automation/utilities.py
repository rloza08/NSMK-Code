#!/usr/bin/env python3
import api.devices as devices
import api.meraki as meraki
import utils.auto_config as config
import utils.auto_globals as auto_globals

"""
Not in use
"""

import csv

def import_csv(fname_csv):

    entries = []
    with open(fname_csv, newline='') as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        for entry in reader:
            entries.append(entry)
    return entries


def deploy_by_netid(netid, serial):
    devices.claimadd(netid, serial)

def deploy(networkName, serial):
    ## FIXME netid = networks.getNetworkId(networkName)
    deploy_by_netid(netid, serial)

def move_admin_users_between_orgs():
    # Read all admin users for org
    # "Albertsons Stores - Group 1")
    orgid_from =  "650207196201616267"
    # "New_Production_MX_Org"
    orgid_to =  "686798943174000779"

    apikey = config.api_key
    auto_globals.load_store()
    orgid = orgid_from
    orgid = orgid_to
    res, users = meraki.getorgadmins(apikey, orgid)
    import utils._json as Json
    users_str = Json.Json.make_pretty(users)
    print(users_str)


    # Now insert into the new org
    for user in users:
        pass
        email = user["email"]
        name = user["name"]
        networks = None
        orgaccess = user["orgAccess"]
        tags = None
        tagaccess = None

        success, result = meraki.addadmin(apikey, orgid, email, name, orgaccess, tags, tagaccess, networks)
        print (success, result)


def list_users():
    # Read all admin users for org
    # "Albertsons Stores - Group 1")
    orgid_from =  "650207196201616267"
    # "New_Production_MX_Org"
    orgid_to =  "686798943174000779"

    apikey = config.api_key
    orgid = orgid_to
    res, users = meraki.getorgadmins(apikey, orgid)
    import utils._json as Json
    users_str = Json.Json.make_pretty(users)
    print(users_str)
    print (len(users))


def move_admin_users():
    # "New_Production_MX_Org"
    orgid = "686798943174000779"
    apikey = config.api_key

    users = import_csv("d:\\org_users.csv")

    # Now insert into the new org
    for user in users:
        email = user["email"]
        name = user["name"]
        networks = None
        orgaccess = user["orgacscess"]
        tags = None
        tagaccess = None

        success, result = meraki.addadmin(apikey, orgid, email, name, orgaccess, tags, tagaccess, networks)
        print (success, result)

def load_fw(fname):
    import json
    json_data = open(fname).read()
    # json_data = json_data.replace("\n","")
    templates = json.loads(json_data)
    #print (templates)

    list_str = "["
    for d in templates:
        convert_fmt = ' "comment": {}, "policy": {}, "protocol": {}, "srcPort": {},' \
        '"srcCidr": {}, "destPort": {}, "destCidr": {}, "syslogEnabled": {}'

        entry_str = convert_fmt.format(d['comment'], d["policy"], d["protocol"], d["srcPort"],
                                    d["srcCidr"], d["destPort"], d["destCidr"], d["syslogEnabled"])
        entry_str = "{"+entry_str+"}"
        list_str += entry_str
    list_str += "]"
    print (list_str)



if __name__ == '__main__':
    load_fw("d:\\firewall_template.json")
