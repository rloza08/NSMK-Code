#!/usr/bin/env python3
import utils.auto_globals as auto_globals
import api.vpn_firewall as vpn_firewall
import utils.auto_logger as l
import automation.bulk_update as bulk
from utils.auto_pmdb import settings
from utils.auto_globals import select_org

"""
Sets up VPN Firewall for a given org

Inputs:
    org_name 

    version   : used to load the vpn firewall rules from   
                /templates/vpn_firewall_rules_<version>.json

    
Output:
    updates the vpn firewall rules for that org id 

"""
import utils.auto_config as auto_config

def deploy(agent, fw_rules):
    # Does physical VLAN creation on meraki device
    org_name = settings["org-name"]
    vpn_firewall._set(org_name, fw_rules)
    l.logger.info("success")

def get(agent):
    org_name = settings["org-name"]
    vpn_firewall._get(org_name)
    l.logger.info("success")

def bulk_update(agent):
    org_name = settings["CLI"]["s2svpnrules-org"]
    settings["agent"] =  agent
    bulk.perform_bulk_update_vpn_firewall(agent, org_name, deploy,  settings["CLI"]["s2svpnrules-version"] )

def bulk_get(agent):
    # Note this org_name is a list not the actual org_name
    org_list = settings["CLI"]["s2svpnrules-org"]
    settings["agent"] =  agent
    bulk.perform_bulk_get_vpn_firewall(agent, org_list, get)


if __name__ == '__main__':
    # auto_globals.select_org(org_name="New_Production_MX_Org")
    # fname = "org-list-New_Production_MX_Org"
    # bulk_update(agent="vpn_firewall_update_bulk", fname=fname, fw_rules=None)
    pass