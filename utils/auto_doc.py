#!/bin/bash/env
""" Module to display all documentation, strings are kept in wiki.py"""
import json
import utils.auto_logger as l
import utils.wiki as wiki
from global_vars import EOM

def json_reader(fpath):
    data = None
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
    # l.logger.debug("data: {}".format(data))
    except Exception as err:
        l.logger.error("fpath:{} {}".format(fpath))
        l.runlogs_logger.error("fpath:{} {}".format(fpath))
    return data


def list_orgs():
    orgs = json_reader("../config/safeway-orgs.json")
    EOM()
    print(" "*38,"ORGS")
    for org in orgs:
        print ("Org:{}\t\t\tId:{}".format(org["name"], org["id"]))
    EOM()


def howto(config=None, templates=None, commands=None, l3_firewall=None, s2s_vpn_rules=None):
    """
    :param config:       Shows how-to for configurations
    :param templates:    Shows how-to for templates (vlans/firewalls)
    :param commands:     Shows how-to for available commands.
    :return:
    """
    EOM()
    print (wiki.howto)
    EOM()
    if config=="config" or config==True:
        print (wiki.howto_config)
    if config==templates or templates==True:
        print (wiki.howto_template)
    if config=="commands" or commands==True:
        print(wiki.howto_commands)
    if config=="l3fw" or l3_firewall==True:
        print(wiki.howto_l3_firewall)
    if config=="s2s-vpn-rules" or s2s_vpn_rules==True:
        print(wiki.howto_s2s_vpn_rules)


def show_status():
    EOM()
    print(wiki.doc)
    import utils.auto_globals as auto_globals
    auto_globals.load_store("orchestration_store")
    EOM()
    print ("org   : {}\n"
           "org-id: {}".format(auto_globals.org_name, auto_globals.orgid))
    netid = auto_globals.netid
    print ("store : {}\n"
           "netid : {}".format(auto_globals.store_name, netid))
    EOM()
    print("_" * 80)


def doc(design=None, automation=None, automation_vlan=None,
            automation_firewall=None, automation_vpn_handler=None,
            api=None, api_vlans=None, api_meraki=None, api_netx=None,
            config=None, utils=None, men_and_mice=None, data=None):

    EOM()
    print(wiki.doc)
    EOM()
    if design == True or design=="design":
        print (wiki.doc_design)
    if automation == True or design=="automation":
        print (wiki.doc_automation)
    if automation_vlan == True or design=="automation_vlan":
        print(wiki.doc_automation_vlan)
    if automation_firewall == True or design=="automation_firewall":
        print(wiki.doc_automation_firewall)
    if automation_vpn_handler == True or design == "automation_vpn_handler":
        print(wiki.doc_automation_vpn_handler)
    if api == True or design == "api":
        print(wiki.doc_api)
    if api_vlans == True or design == "api_vlans":
        print(wiki.doc_api_vlans)
    if api_meraki == True or design == "api_meraki":
        print(wiki.doc_api_meraki)
    if api_netx == True or design == "api_netx":
        print(wiki.doc_api_netx)
    if config == True or design == "config":
        print(wiki.doc_config)
    if utils == True or design == "utils":
        print(wiki.doc_utils)
    if men_and_mice == True or design == "men_and_mice":
        print(wiki.doc_men_and_mice)
    if data == True or design =="data":
        print(wiki.doc_data)

if __name__ == '__main__':
    pass