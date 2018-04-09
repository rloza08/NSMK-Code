#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_logger as l
from api.meraki_patch import meraki
import traceback
import utils.auto_globals as auto_globals
import utils.auto_json as Json

"""
    We only want to load the networks once to save time.
    So Networks Class is made a singleton
"""
class Networks(object):
    def __init__(self):
        success, self.stores = self.list()
        if not success:
            l.logger.error("failed. orgid:{} storeName:{}".format(auto_globals.orgid, storeName))
            assert(0)

    def list(self):
        success = False
        self.networks=None
        try:
            success, self.networks = meraki.getnetworklist(config.api_key, auto_globals.orgid)
            if success:
                l.logger.debug("success")
                l.logger.debug(Json.make_pretty(self.networks))
            else:
                l.logger.error("failed.")
                l.logger.error("networks: {}".format(self.networks))
                assert (0)
        except Exception as err:
            l.logger.error("orgid: {}".format(auto_globals.orgid))
            traceback.print_tb(err.__traceback__)
            assert (0)
        return success, self.networks

    def get_netid_for_store(self, storeName):
        netid=None
        for store in self.stores:
            if store["name"] == storeName:
                netid=store["id"]
                break

        l.logger.debug(netid)
        return netid

    def getdetail(self, networkid):
        success = False
        self.network=None
        try:
            success, self.network= meraki.getnetworkdetail(config.api_key, networkid)
            l.logger.debug(Json.make_pretty(self.network))
            if not success:
                l.logger.error("failed")
                assert(0)
        except Exception as err:
            l.logger.error("orgid: {}".format(networkid))
            traceback.print_tb(err.__traceback__)
            assert(0)
        return success, self.network

    def update(self, networkid, name):
        success = False
        self.network=None
        try:
            success, self.network = meraki.updatenetwork(config.api_key, networkid, name, tz="US/Pacific", tags=None)
            l.logger.debug(Json.make_pretty(self.network))
            if not success:
                l.logger.error("failed")
                assert(0)
        except Exception as err:
            l.logger.error("orgid: {}".format(networkid))
            traceback.print_tb(err.__traceback__)
            assert(0)
        return success, self.network

    @classmethod
    def add(self, orgid, name, nettype):
        success = False
        self.network = None
        try:
            clone_id = config.get_clone_id(orgid)

            success, self.network = meraki.addnetwork(config.api_key, orgid, name, nettype,
                                                      tags=None, tz="US/Pacific",
                                                      cloneid=clone_id, suppressprint=False)
            if not success:
                l.logger.error("failed, {} {}: {}".format(name, nettype, self.network))
                l.store_orchestration_logger.error("failed, {} {}: {}".format(name, nettype, self.network))
                exit(-1)
            l.logger.debug("cloned network, {} {}: {}".format(name, nettype, self.network))
        except  Exception as err:
            l.store_orchestration_logger.error("orgid:{} name:{} nettype:{}".format(orgid, name, nettype))
            traceback.print_tb(err.__traceback__)
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
                assert(0)
        except Exception as err:
            l.logger.error("networid:{} {}".format(networkid, str))
            traceback.print_tb(err.__traceback__)
            assert(0)
        return success, str

def getCreatedNetworkId(networkName):
    fname = "network_{}".format(networkName)
    network = Json.reader(fname)
    if network is None:
        l.logger.error("unable to load rules from firewall_template")
        assert(0)
    return network["id"]

def create(org_id, store_name):
    """Creates a networks and returns a network id"""
    success, netid = Networks.add(org_id, store_name, nettype="appliance")
    return success, netid

def list():
    """List all networks"""
    obj=Networks()
    obj.list()


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
