#!/usr/bin/env python3
import utils.auto_logger as l
from api.network import create, network_list
import utils.auto_globals as auto_globals
import automation.bulk_update as bulk
import utils.auto_json as json
import utils.auto_config as config
from utils.auto_utils import is_valid_store_name
from utils._json import Json


def deploy(agent):
    l.logger.debug("clone network")
    org_name = auto_globals.org_name
    org_id = auto_globals.get_orgid(org_name)
    store_name = auto_globals.store_name
    create(org_id, store_name)
    return


def get_store_lists(agent):
    auto_globals.get_settings()
    org_name = auto_globals.store_lists_org.split("org-")[1]
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
        l.logger.info("created {}".format(fname))
        l.runlogs_logger.info("created {}".format(fname))

    return store_list


def bulk_deploy_networks_for_all_orgs(agent):
    org_group = auto_globals.networks_org
    store_list = auto_globals.networks_store_list

    l.runlogs_logger.info("deploy networks <starting>")

    org_list = json.reader(org_group,"templates")
    orglist = json.make_pretty(org_list)

    l.logger.info("org   list: {}".format(orglist))
    l.logger.info("store list: {}".format(store_list))

    for org in org_list:
        org_name = org["org_name"]
        auto_globals.select_org(org_name)
        l.runlogs_logger.info("selected org: {}".format(org_name))
        l.runlogs_logger.info("using clone source: {}".format(auto_globals.networks_clone_source))

        # Now get the netid for the clone_source
        auto_globals.select_store(auto_globals.networks_clone_source)
        auto_globals.load_store(agent)
        config.set_clone_id(auto_globals.netid)

        bulk.perform_bulk_deploy_networks(agent, deploy, org_name, store_list)
    l.runlogs_logger.info("deploy networks <finished>")


if __name__ == '__main__':
    auto_globals.org_name = "AutomationTestOrg_DONOTDELETE"
    store_list = get_store_list("network-handler")
    print (store_list)