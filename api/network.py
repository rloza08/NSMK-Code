#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_logger as l
from api.meraki_patch import meraki
import utils.auto_globals as auto_globals
import utils.auto_json as Json
import global_vars as gv

"""
    We only want to load the networks once to save time.
    So Networks Class is made a singleton
"""
class Networks(object):
    def __init__(self, org_id=None):
        if org_id == None:
            org_id = auto_globals.orgid
        success, self.stores = self.list(org_id)
        if not success:
            l.logger.error("failed. orgid:{}".format(org_id))
            l.runlogs_logger.error("failed. orgid:{}".format(org_id))
            gv.fake_assert()

    @classmethod
    def list(self, org_id):
        success = False
        networks = None
        import api.meraki
        try:
            success, networks = meraki.getnetworklist(config.api_key, org_id)
            if success:
                l.logger.debug("success")
                l.logger.debug(Json.make_pretty(networks))
            else:
                l.logger.error("failed.")
                l.logger.error("networks: {}".format(networks))
                gv.fake_assert()

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            l.logger.error("orgid: {}    Meraki error: {}".format(org_id, err.default))
            l.runlogs_logger.error("orgid: {}    Meraki error: {}".format(org_id, err.default))

        except Exception as err:
            l.logger.error("orgid: {}".format(org_id))
            l.runlogs_logger.error("orgid: {}".format(org_id))
            gv.fake_assert()
        return success, networks

    def get_netid_for_store(self, storeName):
        netid=None
        for store in self.stores:
            if store["name"] == storeName:
                netid=store["id"]
                break

        l.logger.debug("store: {} netid:{}".format(storeName, netid))
        return netid

    def getdetail(self, networkid):
        success = False
        self.network=None
        try:
            success, self.network= meraki.getnetworkdetail(config.api_key, networkid)
            l.logger.debug(Json.make_pretty(self.network))
            if not success:
                l.logger.error("failed: {}".format(self.network))
                l.runlogs_logger.error("failed: {}".format(self.network))
                gv.fake_assert()
        except Exception as err:
            l.logger.error("networkid: {} {}".format(networkid, self.network))
            l.runlogs_logger.error("networkid: {} {}".format(networkid, self.network))
            gv.fake_assert()
        return success, self.network

    def update(self, networkid, name):
        success = False
        self.network=None
        try:
            success, str = meraki.updatenetwork(config.api_key, networkid, name, tz="US/Pacific", tags=None)
            self.network = str
            l.logger.debug(Json.make_pretty(self.network))
            if not success:
                l.logger.error("{}".format(str))
                l.runlogs_logger.error("{}".format(str))
                gv.fake_assert()
        except Exception as err:
            l.logger.error("orgid: {}".format(networkid))

            gv.fake_assert()
        return success, self.network

    @classmethod
    def add(self, orgid, name, nettype):
        success = False
        self.network = None
        try:
            clone_id = config.get_clone_id()

            success, self.network = meraki.addnetwork(config.api_key, orgid, name, nettype,
                                                      tags=None, tz="US/Pacific",
                                                      cloneid=clone_id, suppressprint=False)
            if not success:
                l.logger.error("failed, {} {}: {}".format(name, nettype, self.network))
                l.runlogs_logger.error("failed, {} {}: {}".format(name, nettype, self.network))
                gv.fake_assert()
            l.logger.debug("cloned network, {} {}: {}".format(name, nettype, self.network))
        except  Exception as err:
            l.logger.error("orgid:{} name:{} nettype:{}".format(orgid, name, nettype))
            l.runlogs_logger.error("orgid:{} name:{} nettype:{}".format(orgid, name, nettype))
            gv.fake_assert()
            assert (0)
        return success, self.network

    def deln(self, networkid):
        success = False
        str=None
        try:
            success, str = meraki.delnetwork(config.api_key, networkid)
            l.logger.debug("success {}".format(networkid))
            if not success:
                l.logger.error("failed, netid: {}".format(networkid))
                gv.fake_assert()
        except Exception as err:
            l.logger.error("networid:{} {}".format(networkid, str))
            l.runlogs_logger.error("networid:{} {}".format(networkid, str))
            gv.fake_assert()
        return success, str

def getCreatedNetworkId(networkName):
    fname = "network_{}".format(networkName)
    network = Json.reader(fname)
    if network is None:
        l.logger.error("unable to load rules from firewall_template")
        l.runlogs_logger.error("unable to load rules from firewall_template")
        gv.fake_assert()
    return network["id"]

def create(org_id, store_name):
    """Creates a networks and returns a network id"""
    success, netid = Networks.add(org_id, store_name, nettype="appliance")
    return success, netid

def network_list(org_id):
    """List all networks"""
    #obj=Networks(org_id)
    success, network_list = Networks.list(org_id)
    return success, network_list

obj_networks=None
def get_store_netid(store_name):
    global obj_networks
    if obj_networks is None:
        obj_networks=Networks()
    netid = obj_networks.get_netid_for_store(store_name)
    return netid

if __name__ == '__main__':
    #create("test_reno116_ubuntu", "appliance")
    #list()
    get_store_netid("SHAWS_9845")
