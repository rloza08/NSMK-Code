#!/usr/bin/env python3
import automation.vlan_handler as vlan_handler
import automation.firewall_handler as firewall_handler
import utils.auto_logger as l
import automation.vpn_handler as vpn_handler
import automation.static_route_handler as static_route_handler
import utils.auto_globals as auto_globals
import utils._csv as Json
import automation.bulk_update as bulk
import utils.auto_json as json
from  utils._json import Json
from automation.vlan_handler import ENTER_ENV_vlans_add, LEAVE_ENV_vlans_add
from automation.vlan_handler import ENTER_ENV_vlans_delete, LEAVE_ENV_vlans_delete

def deploy_vlans_delete(agent, netid, vlans_list):
    vlan_handler.vlans_delete(netid, vlans_list)

def deploy_vlans_add(agent, netid=None, vlans_list=None):
    vlan_handler.deploy_new()

def deploy(agent, netid=None, vlans_list=None):
    l.runlogs_logger.info("vlan setup")

    vlan_handler.deploy()

    l.runlogs_logger.info("static route setup")
    static_route_handler.add()

    l.runlogs_logger.info("l3 firewall setup")
    fw_rules = "{}".format(auto_globals.sites_l3fwrules_version)
    firewall_handler.deploy(agent, fw_rules)

    l.runlogs_logger.info("s2s vpn setup")
    vpn_handler.setupSiteToSiteVpn()

    l.logger.info("success")

def LEAVE_CONTEXT(agent):
    if agent == "cli-deploy-vlans-add":
        LEAVE_ENV_vlans_add()
    elif agent == "cli-deploy-vlans-delete":
        LEAVE_ENV_vlans_delete()

def ENTER_CONTEXT(agent):
    vlans_list = None


    if agent == "cli-deploy-vlans-add":
        vlans_add_list_contents = ENTER_ENV_vlans_add()
        org_group = auto_globals.vlans_add_org
        store_list = auto_globals.vlans_add_store_list
        from utils.auto_utils import show_vlans_add_list
        show_vlans_add_list(vlans_add_list_contents)
        vlans_list = vlans_add_list_contents
    elif agent == "cli-deploy-vlans-delete":
        vlans_delete_list_contents = ENTER_ENV_vlans_delete()
        org_group = auto_globals.vlans_delete_org
        store_list = auto_globals.vlans_delete_store_list
        from utils.auto_utils import show_vlans_delete_list
        show_vlans_delete_list(vlans_delete_list_contents)
        vlans_list  = vlans_delete_list_contents
    else:
        import api.men_and_mice as men_and_mice
        men_and_mice.get_vlan_funnel()
        org_group = auto_globals.networks_org
        store_list = auto_globals.networks_store_list

    fname = store_list
    from utils.auto_utils import show_store_list
    store_list_json = Json.reader(fname, "templates")
    show_store_list(store_list_json)


    return org_group, store_list, vlans_list

def bulk_update(agent, vlans_only=False):
    l.runlogs_logger.info("bulk update started")
    org_group, store_list, vlans_list = ENTER_CONTEXT(agent)

    org_list = json.reader(org_group,"templates")

    if agent == "cli-deploy-stores":
        fw_rules = auto_globals.site_l3fwrules_version
    else:
        fw_rules = None

    for org in org_list:
        org_name = org["org_name"]
        auto_globals.select_org(org_name)
        l.runlogs_logger.info("selected org: {}".format(org_name))

        if agent == "cli-deploy-vlans-delete":
            bulk.perform_bulk_update_store(agent, org_name, store_list, deploy_vlans_delete, vlans_list)
        elif agent == "cli-deploy-vlans-add":
            bulk.perform_bulk_update_store(agent, org_name, store_list, deploy_vlans_add)
        else:
            l.runlogs_logger.info("selected l3fwrules : {}".format(fw_rules))
            bulk.perform_bulk_update_store(agent, org_name, store_list, deploy)

    l.runlogs_logger.info("bulk update finished")
    LEAVE_CONTEXT(agent)

if __name__ == '__main__':
    l.logger.info ("Please setup environment variables if needed:"
           "For Windows under Settins/System Properties/Advanced/Environment Variables"
           "Always restart Pycharm after a change."         
           "PROXY_USER , PROXY_PWD")

    l.runlogs_logger.info ("Use the link below for json to csv and csv to json conversions.")
    l.runlogs_logger.info ("http://www.csvjson.com/csv2json")

    agent = "store_orchestration_bulk"

    bulk_update(agent, fname="store-list-AutomationTest", org_name="org-AutomationTestOrg_DONOTDELETE")
