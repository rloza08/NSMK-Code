#!/usr/bin/env python3
import utils.auto_logger as l
import  utils._csv as Csv
from  utils._json import Json
import utils.auto_globals as auto_globals
from utils.auto_utils import goahead_confirm
from utils.auto_utils import  show_store_list, show_orglist, show_selected_s2svpnrules, show_selected_l3fwrules
import utils.auto_utils as utils
import os
from global_vars import log_verbose as l_verbose
import global_vars as gv

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
            l.firewall_logger.error(str)
            l.logger.error(str)
            gv.fake_assert()
        auto_globals.select_store(store_name)
        auto_globals.load_store(agent)
        try:
            str = ('deploying l3fwrules to {}'.format(store_name))
            l.firewall_logger.info(str)
            fn_deploy(agent, fw_rules)
            str = ('deployed l3fwrules to {}'.format(store_name))
            l.logger.info(str)
            l.firewall_logger.info(str)
        except:
            str = "failed deployment for store : {}".format(store_name)
            l.logger.error(str)
            l.firewall_logger.error(str)
            gv.fake_assert()

def perform_bulk_get_firewall(agent, fn_get, org_name, store_list):
    fname=store_list
    store_list = Json.reader(fname, "templates")

    for store in store_list:
        store_name = store.get("name", None)
        if store_name is None:
            str ="fname: {} ::: name field was not found for store {}".format(fname, store)
            l.firewall_logger.error(str)
            l.logger.error(str)
            gv.fake_assert()
        auto_globals.select_store(store_name)
        auto_globals.load_store(agent, minimum=True)
        try:
            str = ('getting l3fwrules for {}'.format(store_name))
            l.logger.info(str)
            l.firewall_logger.info(str)
            fn_get(agent)
            str = ('got l3fwrules for {}'.format(store_name))
            l.logger.info(str)
            l.firewall_logger.info(str)
        except:
            str = "failed getting l3fwrules for store : {}".format(store_name)
            l.logger.error(str)
            l.firewall_logger.error(str)
            gv.fake_assert()


def perform_bulk_update_store(agent, org_name, fname, fn_deploy):
    store_list = Json.reader(fname, "templates")

    if not goahead_confirm("stores"):
        return

    for store in store_list:
        store_name = store.get("name", None)
        l.store_orchestration_logger.info("deploying network: {}".format(store_name))
        if store_name is None:
            str = "fname: {} ::: store_name field was not found for store {}".format(fname, store)
            l.logger.error(str)
            gv.fake_assert()
        l.logger.info("deploying store : {}".format(store_name))
        auto_globals.select_store(store_name)
        auto_globals.load_store(agent)
        fn_deploy(agent)
        l.logger.info("deployed store : {}".format(store_name))
        Json.writer(fname, store_list, "templates")
        Csv.transform_to_csv(fname, None, path="templates")
        l.store_orchestration_logger.info("deployed network: {}  netid: {}".format(store_name, auto_globals.netid))


def perform_bulk_deploy_networks(agent, fn_deploy, org_name, store_list_file):
    store_list = Json.reader(store_list_file, "templates")
    show_store_list(store_list)

    if not goahead_confirm("stores"):
        return

    for store in store_list:
        store_name = store.get("name", None)
        if store_name is None:
            l.logger.error("fname: {} ::: name field was not found for store {}".format(store))
            gv.fake_assert()
        l.store_orchestration_logger.info("created network : {}".format(store_name))

        auto_globals.select_store(store_name)
        fn_deploy(agent)
        l.logger.info("created network : {}".format(store_name))

def perform_bulk_update_vpn_firewall(agent, fname, fn_deploy, rules=None):
    l.vpn_firewall_logger.info("deploying {}".format(agent))
    org_list = Json.reader(fname, "templates")
    Csv.transform_to_csv(fname, None, path="templates")

    org_name = org_list[0].get("org_name", None)
    auto_globals.load_org(agent)
    auto_globals.select_org(org_name)
    str = "selected org: {}".format(org_name)
    l.logger.info(str)
    l.firewall_logger.info(str)

    vpn_rules = auto_globals.s2svpnrules_version
    str = "vpns2srules version: {}".format(vpn_rules)
    l.logger.info(str)
    l.vpn_firewall_logger.info(str)

    if not goahead_confirm("s2svpnrules"):
        return

    if org_name is None:
        l.logger.error("failed deploying s2svpnrules to org: {}".format(org_name))
        l.vpn_firewall_logger.error("failed deploying s2svpnrules to org: {}".format(org_name))
        gv.fake_assert()
    try:
        l.logger.info("deploying vpns2srules to org: {}".format(vpn_rules, org_name))
        l.vpn_firewall_logger.info("deploying vpns2srules to org: {}".format(org_name))
        fn_deploy(agent, rules)
    except:
        str = "failed deploying s2svpnrules {} to org: {}".format(rules, org_name)
        l.logger.error(str)
        l.vpn_firewall_logger.info(str)
        gv.fake_assert()
    str = 'deployed s2svpnrules: "{}" to org: "{}"'.format(rules, org_name )
    l.logger.info(str)
    l.vpn_firewall_logger.info(str)

def perform_bulk_get_vpn_firewall(agent, fname, fn_get):
    l.vpn_firewall_logger.info("downloading {}".format(agent))
    org_list = Json.reader(fname, "templates")
    Csv.transform_to_csv(fname, None, path="templates")

    org_name = org_list[0].get("org_name", None)

    auto_globals.load_org(agent)
    auto_globals.select_org(org_name)

    if org_name is None:
        str = "org {} not found".format(org_name)
        l.logger.error(str)
        l.vpn_firewall_logger.error(str)
        gv.fake_assert()
    utils.create_org_data_dir(agent)
    try:
        str = "downloading vpns2srules for org: {}".format(org_name)
        l.logger.info(str)
        l.vpn_firewall_logger.info(str)
        fn_get(agent)
    except:
        str = "failed obtaining s2svpnrules for org: {}".format(org_name)
        l.logger.error(str)
        l.vpn_firewall_logger.info(str)
        gv.fake_assert()
    str = 'downloaded s2svpnrules for org : "{}"'.format(org_name )
    l.logger.info(str)
    l.vpn_firewall_logger.info(str)
