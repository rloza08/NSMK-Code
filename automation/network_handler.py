#!/usr/bin/env python3
import utils.auto_logger as l
from api.network import create
import utils.auto_globals as auto_globals
import automation.bulk_update as bulk
import utils.auto_json as json
from utils.auto_utils import show_orglist
import utils.auto_config as config

def deploy(agent):
    l.logger.debug("clone network")
    org_name = auto_globals.org_name
    org_id = auto_globals.get_orgid(org_name)
    store_name = auto_globals.store_name
    create(org_id, store_name)
    return


def bulk_deploy_networks_for_all_orgs(agent):
    org_group = auto_globals.deploy_org
    store_list = auto_globals.deploy_store_list

    l.runlogs_logger.info("deploy networks <starting>")

    org_list = json.reader(org_group,"templates")
    orglist = json.make_pretty(org_list)

    l.logger.info("org   list: {}".format(orglist))
    l.logger.info("store list: {}".format(store_list))

    for org in org_list:
        org_name = org["org_name"]
        auto_globals.select_org(org_name)
        l.runlogs_logger.info("selected org: {}".format(org_name))
        l.runlogs_logger.info("using clone source: {}".format(auto_globals.deploy_clone_source))

        # Now get the netid for the clone_source
        auto_globals.select_store(auto_globals.deploy_clone_source)
        auto_globals.load_store(agent)
        config.set_clone_id(auto_globals.netid)

        bulk.perform_bulk_deploy_networks(agent, deploy, org_name, store_list)
    l.runlogs_logger.info("deploy networks <finished>")


if __name__ == '__main__':
    bulk_deploy_networks_for_all_orgs(agent="network_handler", org_group="Org-AutomationTestOrg_DONOTDELETE", store_list="Store-List-AutomationTest")
