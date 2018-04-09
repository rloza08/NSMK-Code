#!/usr/bin/env python3
import automation.vlan_handler as vlan_handler
import automation.firewall_handler as firewall_handler
import utils.auto_logger as l
import automation.vpn_handler as vpn_handler
import automation.static_route_handler as static_route_handler
import utils.auto_globals as auto_globals
import utils.auto_json as auto_json
import utils._csv as Csv
import utils._csv as Json
import automation.bulk_update as bulk
import utils.auto_json as json
from  utils._json import Json

def deploy(agent):

    l.store_orchestration_logger.info("vlan setup")
    vlan_handler.deploy()

    l.store_orchestration_logger.info("static route setup")
    static_route_handler.add()

    l.store_orchestration_logger.info("l3 firewall setup")
    fw_rules = "{}".format(auto_globals.deploy_l3fwrules_version)
    firewall_handler.deploy(agent, fw_rules)

    production = auto_globals.production
    production = True
    if production:
        l.store_orchestration_logger.info("s2s vpn setup")
        vpn_handler.setupSiteToSiteVpn()

    l.logger.info("success")

def bulk_update(agent):
    org_group = auto_globals.deploy_org
    store_list = auto_globals.deploy_store_list

    l.store_orchestration_logger.info("bulk update started")
    org_list = json.reader(org_group,"templates")
    from utils.auto_utils import show_orglist, show_store_list, show_selected_l3fwrules, show_selected_s2svpnrules
    fname=store_list
    store_list_json = Json.reader(fname, "templates")

    fw_rules = auto_globals.deploy_l3fwrules_version

    for org in org_list:
        org_name = org["org_name"]
        auto_globals.select_org(org_name)
        l.firewall_logger.info("selected org: {}".format(org_name))
        l.firewall_logger.info("selected l3fwrules : {}".format(fw_rules))
        show_store_list(store_list_json)

        bulk.perform_bulk_update_store(agent, org_name, store_list, deploy)
        l.store_orchestration_logger.info("finished for org: {}".format(org_name))
    l.store_orchestration_logger.info("bulk update finished")

if __name__ == '__main__':
    l.logger.info ("Please setup environment variables if needed:"
           "For Windows under Settins/System Properties/Advanced/Environment Variables"
           "Always restart Pycharm after a change."         
           "PROXY_USER , PROXY_PWD")

    l.store_orchestration_logger.info ("Use the link below for json to csv and csv to json conversions.")
    l.store_orchestration_logger.info ("http://www.csvjson.com/csv2json")

    agent = "store_orchestration_bulk"

    bulk_update(agent, fname="Store-List-AutomationTest", org_name="Org-AutomationTestOrg_DONOTDELETE")
