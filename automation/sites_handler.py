#!/usr/bin/env python3
import automation.vlan_handler as vlan_handler
import automation.firewall_handler as firewall_handler
import utils.auto_logger as l
import automation.vpn_handler as vpn_handler
import automation.static_route_handler as static_route_handler
import utils.auto_globals as auto_globals
import utils.low_csv as Json
import automation.bulk_update as bulk
import utils.auto_json as json
from utils.low_json import Json
from automation.vlan_handler import ENTER_ENV_vlans_delete, LEAVE_ENV_vlans_delete
from utils.auto_pmdb import settings


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
    fw_rules = "{}".format(settings["CLI"]["sites-l3fwrules-version"])
    firewall_handler.deploy(agent, fw_rules)

    l.runlogs_logger.info("s2s vpn setup")
    vpn_handler.setupSiteToSiteVpn()

    l.logger.info("success")


def LEAVE_CONTEXT(agent):
    if agent == "cli-deploy-vlans-add":
        pass
    elif agent == "cli-deploy-vlans-delete":
        LEAVE_ENV_vlans_delete()


def ENTER_CONTEXT(agent):
    vlans_list = None

    if agent == "cli-deploy-vlans-add":
        org_group = settings["CLI"]["vlans-add-org"]
        store_list = settings["CLI"]["vlans-add-store-list"]
        from utils.auto_utils import show_vlans_add_list
        show_vlans_add_list()
        vlans_list = settings["vlans-add-list"]
    elif agent == "cli-deploy-vlans-delete":
        vlans_delete_list_contents = ENTER_ENV_vlans_delete()
        org_group = settings["CLI"]["vlans-delete-org"]
        store_list = settings["CLI"]["vlans-delete-store-list"]
        from utils.auto_utils import show_vlans_delete_list
        show_vlans_delete_list(vlans_delete_list_contents)
        vlans_list = vlans_delete_list_contents
    else:
        org_group = settings["CLI"]["networks-org"]
        store_list = settings["CLI"]["networks-store-list"]

    fname = store_list
    from utils.auto_utils import show_store_list
    store_list_json = Json.reader(fname, "templates")
    show_store_list(store_list_json)

    return org_group, store_list, vlans_list

def bulk_update_vlans(agent, vlans_only=False):
    bulk_update(agent, vlans_only=True)

def bulk_update_sites(agent, vlans_only=False):
    bulk_update(agent)


def bulk_update(agent, vlans_only=False):
    l.runlogs_logger.info("bulk update started")
    org_group, store_list, vlans_list = ENTER_CONTEXT(agent)
    org_list = json.reader(org_group, "templates")

    assert(agent in ["cli-deploy-vlans-add", "cli-deploy-vlans-delete", "cli-deploy-sites", "cli-deploy-l3fwrules"])
    for org in org_list:
        org_name = org["org_name"]
        auto_globals.select_org(org_name)
        l.runlogs_logger.info("selected org: {}".format(org_name))

        if agent == "cli-deploy-vlans-delete":
            bulk.perform_bulk_update_store(agent, org_name, store_list, deploy_vlans_delete, vlans_list)
        elif agent == "cli-deploy-vlans-add":
            bulk.perform_bulk_update_store(agent, org_name, store_list, deploy_vlans_add)
        else:
            if agent in ["cli-deploy-sites", "cli-deploy-l3fwrules"]:
                fw_rules = settings["CLI"]["sites-l3fwrules-version"]
                l.runlogs_logger.info("selected l3fwrules : {}".format(fw_rules))

            bulk.perform_bulk_update_store(agent, org_name, store_list, deploy)

    l.runlogs_logger.info("bulk update finished")
    LEAVE_CONTEXT(agent)


if __name__ == '__main__':
    l.logger.info("Please setup environment variables if needed:"
                  "For Windows under Settins/System Properties/Advanced/Environment Variables"
                  "Always restart Pycharm after a change."
                  "PROXY_USER , PROXY_PWD")

    l.runlogs_logger.info("Use the link below for json to csv and csv to json conversions.")
    l.runlogs_logger.info("http://www.csvjson.com/csv2json")

    agent = "store_orchestration_bulk"

    bulk_update(agent, fname="store-list-AutomationTest", org_name="org-AutomationTestOrg_DONOTDELETE")
