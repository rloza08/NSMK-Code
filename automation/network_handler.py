#!/usr/bin/env python3
import utils.auto_logger as l
from api.network import create, network_list
import utils.auto_globals as auto_globals
import automation.bulk_update as bulk
import utils.auto_json as json
import utils.auto_config as config
from utils.auto_utils import is_valid_store_name
from utils.low_json import Json
from utils.auto_pmdb import settings
from api.devices import deploy_serials


def deploy(agent):
    l.logger.debug("clone network")
    org_name = settings["org-name"]
    org_id = auto_globals.get_orgid(org_name)
    store_name = settings["store-name"]
    success, network = create(org_id, store_name)
    if success:
        settings["network"] = network
        settings["netid"] = network["id"]
    return success

import copy
def get_store_lists(agent):
    settings["orchestration-agent"] = agent
    org_name = settings["CLI"]["store-lists-org"].split("org-")[1]
    settings["org-name"] = org_name
    auto_globals.set_settings()
    l.logger.info("creating store lists for org {}".format(org_name))
    l.runlogs_logger.info("creating store lists for org {}".format(org_name))
    org_id = auto_globals.get_orgid(org_name)
    success, store_list = network_list(org_id)
    if success is False:
        return False
    stores = {}
    stores["ALL"]=[]
    it = {}
    from copy import deepcopy
    for item in store_list:
        name = item["name"]
        valid, store_name, group, store_number = is_valid_store_name(name)
        if not valid:
            continue
        it["name"]= store_name
        stores["ALL"].append(deepcopy(it))
        if group not in stores.keys():
            stores[group] = []
        stores[group].append(deepcopy(it))
    for group in stores.keys():
        fname = "store-list-{}-{}".format(org_name, group)
        Json.writer(fname, data=stores[group], path="../templates")
        l.logger.info("created {} with {} stores.".format(fname, len(stores[group])))
        l.runlogs_logger.info("created {} with {} stores.".format(fname, len(stores[group])))

    return store_list


def bulk_deploy_networks_for_all_orgs(agent):
    org_group = settings["CLI"]["networks-org"]
    store_list = settings["CLI"]["networks-store-list"]
    serials_list = settings.get("CLI").get("networks-serials")
    l.runlogs_logger.info("deploy networks <starting>")

    org_list = json.reader(org_group, "templates")
    orglist = json.make_pretty(org_list)

    l.logger.info("org   list: {}".format(orglist))
    l.logger.info("store list: {}".format(store_list))
    l.logger.info("serials list: {}".format(serials_list))

    for org in org_list:
        org_name = org["org_name"]
        auto_globals.select_org(org_name)
        l.runlogs_logger.info("selected org: {}".format(org_name))
        l.runlogs_logger.info("using clone source: {}".format(settings["CLI"]["networks-clone-source"]))
        l.runlogs_logger.info("using serials : {}".format(settings.get("CLI").get("networks-serials")))

        # Now get the netid for the clone_source
        store_name = settings["CLI"]["networks-clone-source"]
        auto_globals.select_store(store_name)
        auto_globals.load_store(agent, store_name)
        config.set_clone_id(settings["netid"])

        bulk.perform_bulk_deploy_networks(agent, deploy, deploy_serials,  store_list)
    l.runlogs_logger.info("deploy networks <finished>")


if __name__ == '__main__':
    settings["org-name"] = "AutomationTestOrg_DONOTDELETE"
    store_list = get_store_lists("network-handler")
    print (store_list)
    pass