#!/usr/bin/env python3
import utils.auto_logger as l
import  utils.low_csv as Csv
from  utils.low_json import Json
import utils.auto_globals as auto_globals
from utils.auto_utils import goahead_confirm
from utils.auto_utils import  show_store_list, show_orglist, show_selected_s2svpnrules, show_selected_l3fwrules
import utils.auto_utils as utils
import global_vars as gv
from utils.auto_pmdb import settings
from api.network import destroy

def perform_bulk_update_firewall(agent, fn_deploy, org_name, fw_rules, store_list):
    fname=store_list
    store_list = Json.reader(fname, "templates")
    """Ensure that the list now has always all the three fields
    in short that it is normalized so csv conversion is not upset"""
    Json.writer(fname, store_list, "templates")
    Csv.transform_to_csv(fname, None, path="templates")

    show_store_list(store_list)

    if not goahead_confirm("l3fwrules"):
        return

    for store in store_list:
        store_name = store.get("name", None)

        if store_name is None:
            str = "fname: {} ::: name field was not found for store {}".format(fname, store)
            l.runlogs_logger.error(str)
            l.logger.error(str)
            gv.fake_assert()
        auto_globals.select_store(store_name)
        try:
            assert(auto_globals.load_store(agent, store_name))
            str = ('deploying l3fwrules to {}'.format(store_name))
            l.runlogs_logger.info(str)
            fn_deploy(agent, fw_rules)
            str = ('deployed l3fwrules to {}'.format(store_name))
            l.logger.info(str)
            l.runlogs_logger.info(str)
        except:
            str = "failed deployment for store : {}".format(store_name)
            l.logger.error(str)
            l.runlogs_logger.error(str)
            gv.fake_assert()

def perform_bulk_get_firewall(agent, fn_get, org_name, store_list):
    fname=store_list
    store_list = Json.reader(fname, "templates")

    for store in store_list:
        store_name = store.get("name", None)
        if store_name is None:
            str ="fname: {} ::: name field was not found for store {}".format(fname, store)
            l.runlogs_logger.error(str)
            l.logger.error(str)
            gv.fake_assert()
        auto_globals.select_store(store_name)
        try:
            success = auto_globals.load_store(agent, store_name)
            assert(success)
            str = ('getting l3fwrules for {}'.format(store_name))
            l.logger.info(str)
            l.runlogs_logger.info(str)
            fn_get(agent)
            str = ('got l3fwrules for {}'.format(store_name))
            l.logger.info(str)
            l.runlogs_logger.info(str)
        except:
            str = "failed getting l3fwrules for store : {}".format(store_name)
            l.logger.error(str)
            l.runlogs_logger.error(str)
            gv.fake_assert()


def perform_bulk_delete_vlans(agent, org_name, fname, fn_deploy, vlans_only=False):
    store_list = Json.reader(fname, "templates")

    if not goahead_confirm("stores"):
        return

    for store in store_list:
        store_name = store.get("name", None)
        l.runlogs_logger.info("deploying network: {}".format(store_name))
        if store_name is None:
            str = "fname: {} ::: store_name field was not found for store {}".format(fname, store)
            l.logger.error(str)
            l.runlogs_logger.error(str)
            gv.fake_assert()
        l.logger.info("deploying store : {}".format(store_name))
        auto_globals.select_store(store_name)
        if (auto_globals.load_store(agent, store_name)) is False:
            l.logger.error("failed deploying network: {}".format(store_name))
            l.runlogs_logger.error("failed deploying network: {}".format(store_name))
            return

        fn_deploy(agent, vlans_only)
        l.logger.info("deployed store : {}".format(store_name))
        Json.writer(fname, store_list, "templates")
        Csv.transform_to_csv(fname, None, path="templates")
        l.runlogs_logger.info("deployed network: {}  netid: {}".format(store_name, settings["netid"]))


def perform_bulk_update_store(agent, org_name, fname, fn_deploy, vlans_list=[]):
    store_list = Json.reader(fname, "templates")

    if not goahead_confirm("stores"):
        return

    for store in store_list:
        store_name = store.get("name", None)
        l.runlogs_logger.info("deploying {}".format(store_name))
        if store_name is None:
            str = "fname: {} ::: store_name field was not found for store {}".format(fname, store)
            l.logger.error(str)
            l.runlogs_logger.error(str)
            gv.fake_assert()
        l.logger.info("deploying store : {}".format(store_name))
        auto_globals.select_store(store_name)
        if (auto_globals.load_store(agent, store_name)) is False:
            l.logger.error("failed deploying {}".format(store_name))
            l.runlogs_logger.error("failed deploying {}".format(store_name))
            return
        netid = settings["netid"]
        fn_deploy(agent, netid, vlans_list)
        Json.writer(fname, store_list, "templates")
        Csv.transform_to_csv(fname, None, path="templates")
        l.runlogs_logger.info("deployed {}".format(store_name))
        l.logger.info("deployed: {}  netid: {}".format(store_name, settings["netid"]))

def perform_bulk_deploy_networks(agent, fn_deploy, fn_deploy_serials, store_list_file):

    store_list = Json.reader(store_list_file, "templates")
    show_store_list(store_list)
    serials_list_file = settings["CLI"]["networks-serials"]
    serials_list = Json.reader(serials_list_file, "templates")

    if not goahead_confirm("stores"):
        return

    for store in store_list:
        store_name = store.get("name", None)
        if store_name is None:
            l.logger.error("fname: {} ::: name field was not found for store {}".format(store))
            l.runlogs_logger.error("fname: {} ::: name field was not found for store {}".format(store))
            gv.fake_assert()
        l.runlogs_logger.info("created network : {}".format(store_name))
        l.logger.info("created network : {}".format(store_name))

        auto_globals.select_store(store_name)
        assert (auto_globals.load_empty_store(agent, store_name))
        if not fn_deploy(agent):
            l.logger.error("failed to create network : {}".format(store_name))
            l.runlogs_logger.error("failed to create network : {}".format(store_name))
            return

        if gv.use_serials:
            serial_count = auto_globals.load_store_serials(store_name, serials_list)
            for count in range(1, serial_count+1):
                settings["serial"] = settings["serial{}".format(count)]
                settings["device-name"] = settings["device-name{}".format(count)]
                l.runlogs_logger.info("adding serial {} to {}".format(settings["serial"], store_name))
                l.logger.info("adding serial {} to {}".format(settings["serial"], store_name))
                if not fn_deploy_serials():
                    if gv.serial_not_available_revert_clone:
                        destroy(netid=settings["netid"])
                    l.logger.error("failed adding serial {} to  network : {}".format(settings["serial"], store_name))
                    l.runlogs_logger.error("failed adding serial {} network : {}".format(settings["serial"], store_name))
                    return
                l.runlogs_logger.info("added serial {} to {}".format(settings["serial"], store_name))
                l.logger.info("added serial {} to {}".format(settings["serial"], store_name))

def perform_bulk_update_vpn_firewall(agent, fname, fn_deploy, rules=None):
    l.runlogs_logger.info("deploying {}".format(agent))
    org_list = Json.reader(fname, "templates")
    Csv.transform_to_csv(fname, None, path="templates")
    org_name = org_list[0].get("org_name", None)
    settings["org-name"] = org_name
    auto_globals.load_org(agent, org_name)
    str = "selected org: {}".format(org_name)
    l.logger.info(str)
    l.runlogs_logger.info(str)

    vpn_rules = settings["CLI"]["s2svpnrules-version"]
    str = "vpns2srules version: {}".format(vpn_rules)
    l.logger.info(str)
    l.runlogs_logger.info(str)

    if not goahead_confirm("s2svpnrules"):
        return

    if org_name is None:
        l.logger.error("failed deploying s2svpnrules to org: {}".format(org_name))
        l.runlogs_logger.error("failed deploying s2svpnrules to org: {}".format(org_name))
        gv.fake_assert()
    try:
        l.logger.info("deploying vpns2srules to org: {}".format(vpn_rules, org_name))
        l.runlogs_logger.info("deploying vpns2srules to org: {}".format(org_name))
        fn_deploy(agent, rules)
    except:
        str = "failed deploying s2svpnrules {} to org: {}".format(rules, org_name)
        l.logger.error(str)
        l.runlogs_logger.info(str)
        gv.fake_assert()
    str = 'deployed s2svpnrules: "{}" to org: "{}"'.format(rules, org_name )
    l.logger.info(str)
    l.runlogs_logger.info(str)

def perform_bulk_get_vpn_firewall(agent, org_list_fname, fn_get):
    l.runlogs_logger.info("downloading {}".format(agent))
    org_list = Json.reader(org_list_fname, "templates")
    Csv.transform_to_csv(org_list_fname, None, path="templates")

    org_name = org_list[0].get("org_name", None)
    auto_globals.load_org(agent, org_name)

    if org_name is None:
        str = "org {} not found".format(org_name)
        l.logger.error(str)
        l.runlogs_logger.error(str)
        gv.fake_assert()
    try:
        str = "downloading vpns2srules for org: {}".format(org_name)
        l.logger.info(str)
        l.runlogs_logger.info(str)
        fn_get(agent)
    except:
        str = "failed obtaining s2svpnrules for org: {}".format(org_name)
        l.logger.error(str)
        l.runlogs_logger.info(str)
        gv.fake_assert()
    str = 'downloaded s2svpnrules for org : "{}"'.format(org_name )
    l.logger.info(str)
    l.runlogs_logger.info(str)
