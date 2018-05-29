#!/usr/bin/env python3
import socket
import utils.auto_json as mkjson
from utils.auto_logger import runlogs_logger, logger
import global_vars as gv
from utils.auto_utils import char_range
from utils.auto_pmdb import settings
from copy import deepcopy

"""
How to generate netx by example

a) ping cc8501
b) Pinging cc8501 [10.218.31.5] with 32 bytes of data:
c) netx["upper"] = {1:10, 2:218, 3:28, 4:0}   (31-3 = 28 for 3rd octet)
d) netx["lower"] = {1:10, 2:154, 3:28, 4:0}   (218-0x40=154 for 2nd octet)

e) next{"a"] = {1:10. 2:218. 3:28}         (copy 1,2,3 octets from netx["upper"]
f) next{"b"] = {1:10. 2:218. 3:29}         (copy 1,2 octets from netx["a"] and 3rd pctect = netx["a"][3] + 1
g) next{"c"] = {1:10. 2:218. 3:30}         (copy 1,2 octets from netx["b"] and 3rd pctect = netx["b"][3] + 1
e) next{"d"] = {1:10. 2:218. 3:31}         (copy 1,2 octets from netx["c"] and 3rd pctect = netx["c"][3] + 1

e) next{"e"] = {1:10. 2:218. 3:28}         (copy 1,2,3 octets from netx["lower"]
f) next{"f"] = {1:10. 2:218. 3:29}         (copy 1,2 octets from netx["a"] and 3rd pctect = netx["f"][3] + 1
g) next{"g"] = {1:10. 2:218. 3:30}         (copy 1,2 octets from netx["b"] and 3rd pctect = netx["g"][3] + 1
e) next{"h"] = {1:10. 2:218. 3:31}         (copy 1,2 octets from netx["c"] and 3rd pctect = netx["b"][3] + 1

So for
ip = 10.218.31.5
netx = {
    "upper": "10.218.28.0",
    "lower": "10.154.28.0",
    "a": "10.218.28",
    "b": "10.218.29",
    "c": "10.218.30",
    "d": "10.218.31",
    "e": "10.154.28",
    "f": "10.154.29",
    "g": "10.154.30",
    "h": "10.154.31",
    "i": "10.121.31",
    "i": "10.77.23"

}

NEW Structure

append to
{
    "upper": "10.218.28.0",
    "lower": "10.154.28.0",
    "new-summary": "10.Y.Z.0"
    "a": "10.218.28",
    "b": "10.218.29",
    "c": "10.218.30",
    "d": "10.218.31",
    "e": "10.154.28",
    "f": "10.154.29",
    "g": "10.154.30",
    "h": "10.154.31"
    "i": "10.Y.Z+0"     ---. Y and Z comes from separate file
    "j": "10.Y.Z+1"
    "k": "10.Y.Z+2"
    "l": "10.Y.Z+3"
}


StoreNumber, Subnet
8951, 10.<Y>.<Z>   e.g.
8952, 10.<Y>.<Z>

e.g.

StoreNumber, Subnet, id
8951, i, 10,11.11
8952, j, 

funnel
 10.

"""
class Netx(object):
    def __init__(self):
        non_netx_range = list(char_range('i', 'z'))
        self.valid_netx_subnet_list = ["a", "b", "c", "d", "e", "f", "g", "h"]
        self.valid_non_netx_subnet_list = non_netx_range
        self.valid_subnet_list = ["a", "b", "c", "d", "e", "f", "g", "h"] + non_netx_range
        pass

    def get_addr(self, host):
        try:
            res = socket.gethostbyname(host)
            return res
        except:
            from utils.auto_config import dryrun_netx_fake_ip, dryrun
            if dryrun:
                return settings["dryrun-netx-fake-ip"]
            logger.error("Cannot reach store/device : {}".format(host))
            runlogs_logger.error("Cannot reach store/device : {}".format(host))
            gv.fake_assert()

    def get_netx_dense(self, host):
        netx = {
            "upper": {}, "lower": {},
            "a": {}, "b": {}, "c": {}, "d": {},
            "e": {}, "f": {}, "g": {}, "h": {}
        }

        ip_str = self.get_addr(host)
        ip = ip_str.split(".")

        netx["upper"][1] = netx["lower"][1] = int(ip[0])
        netx["upper"][2] = int(ip[1])
        netx["upper"][3] = netx["lower"][3] = int(ip[2]) - 3
        netx["upper"][4] = netx["lower"][4] = 0

        netx["lower"][2] = int(ip[1]) - 0x40

        netx["a"][1] = netx["b"][1] = netx["c"][1] = netx["d"][1] = int(ip[0])
        netx["a"][2] = netx["b"][2] = netx["c"][2] = netx["d"][2] = int(ip[1])

        netx["e"][1] = netx["f"][1] = netx["g"][1] = netx["h"][1] = int(ip[0])
        netx["e"][2] = netx["f"][2] = netx["g"][2] = netx["h"][2] = int(ip[1]) - 0x40

        netx["a"][3] = netx["e"][3] = int(ip[2]) - 3
        netx["b"][3] = netx["f"][3] = int(ip[2]) - 2
        netx["c"][3] = netx["g"][3] = int(ip[2]) - 1
        netx["d"][3] = netx["h"][3] = int(ip[2])

        return netx

    def get_nnetx_dense(self, host):
        nn_map = settings.get("NON-NETX")
        if nn_map is None:
            return None

        store_number = int(settings["store-number"])
        entries = self.valid_non_netx_subnet_list
        nnetx = dict()
        # Essentially create the dictionary of dictionaries
        for entry in entries:
            nnetx[entry] = {}
        nnetx["non-netx-summary"] = None


        nnetx_inputs = nn_map.get(store_number)
        if nnetx_inputs is None:
            logger.error("no non_netx_info for store number {}".format(store_number))
            runlogs_logger.error("no non_netx_info for store number {}".format(store_number))
            gv.fake_assert()

        # Summary repeasts for all subnets and is only added once
        nnetx_input = nnetx_inputs[0]
        summary = nnetx_input["Summary"]
        nn = dict()
        nn["non-netx-summary"] = deepcopy(summary)

        # Get subnets
        for nnetx_input in nnetx_inputs:
            funnel_subnet = nnetx_input["FunnelSubnet"]
            index = funnel_subnet.split(".")[2]
            assert(index in self.valid_non_netx_subnet_list)

            # Validate
            if summary != nnetx_input["Summary"]:
                logger.error("summary mismatch : {}\n{}", summary, nn_input["Summary"])
                exit(-1)

            entry = nnetx_input["ActualSubnet"]
            octets = entry.split(".")
            nn[index] = dict()
            nn[index][1] = int(octets[0])
            nn[index][2] = int(octets[1])
            nn[index][3] = int(octets[2])

        return nn

    def get_netx_str(self, netx):
        netx_str = {
            "upper": "0.0.0.0",
            "lower": "0.0.0.0",
            "a": "0.0.0", "b": "0.0.0", "c": "0.0.0", "d": "0.0.0",
            "e": "0.0.0", "f": "0.0.0", "g": "0.0.0", "h": "0.0.0"
        }

        netx_str["upper"] = "{}.{}.{}.{}".format(netx["upper"][1], netx["upper"][2], netx["upper"][3], netx["upper"][4])
        netx_str["lower"] = "{}.{}.{}.{}".format(netx["lower"][1], netx["lower"][2], netx["lower"][3], netx["lower"][4])

        netx_to_str = lambda netx, idx: "{}.{}.{}".format(netx[idx][1], netx[idx][2], netx[idx][3])

        for idx in self.valid_netx_subnet_list:
            netx_str[idx] = netx_to_str(netx, idx)

        return netx_str


    def get_nnetx_str(self, nnetx):
        if nnetx is None:
            return None
        nnetx_str = dict()

        nnetx_str["non-netx-summary"] = deepcopy(nnetx["non-netx-summary"])

        nnetx_to_str = lambda nnetx, idx: "{}.{}.{}".format(nnetx[idx][1], nnetx[idx][2], nnetx[idx][3])

        for key in nnetx.keys():
            if key in self.valid_non_netx_subnet_list :
                nnetx_str[key] = nnetx_to_str(nnetx, key)

        return nnetx_str


    def get_netx(self, host):
        # Gets the netx info in a more pythonic format
        self.netx_dense = self.get_netx_dense(host)
        self.nnetx_dense = self.get_nnetx_dense(host)
        self.netx_str = self.get_netx_str(self.netx_dense)
        self.nnetx_str = self.get_nnetx_str(self.nnetx_dense)

        if self.nnetx_dense is None:
            return self.netx_str

        netx_str_all = {**self.netx_str, **self.nnetx_str}
        return netx_str_all


def get(host):
    obj = Netx()
    netx_obj = obj.get_netx(host)
    return netx_obj


from utils.auto_globals import load_store, load_org
from api.meraki_patch import init_meraki_patch
def netx_test():
    init_meraki_patch()
    _orchestration_agent = "cli-test"
    org_name = "AutomationTestOrg_DONOTDELETE"
    load_org(_orchestration_agent, org_name)
    load_store("agent-secret", "8501")
    netx = get("cc8501")
    str = mkjson.make_pretty((netx))
    print(str)


if __name__ == '__main__':
    pass
