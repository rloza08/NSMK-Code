#!/usr/bin/env python3
import utils.auto_json as json
import utils.auto_logger as log
import utils.auto_config as config
import api.static_route as static_route
import automation.vlan_handler as vlan_handler
from utils.auto_pmdb import settings


def add(summary_only=False):
    """
    Adds upper, lower static routes and non-netx-summary

    Inputs:
        upper subnet
        lower subnet
        non-netx-summary
        vlans_generate_<netid> file

    Outputs:


        add via /api/static_route (lower_subnet, ip)
        add via /api/static_route (upper_subnet, ip)

    """
    fname, lower, upper, nnetx_summary = vlan_handler.createVlanFiles()
    log.logger.debug(fname)

    # Get the ip from the vlans_generated file
    vlans = json.reader(fname.split(".")[0])
    ip = None
    for vlan in vlans:
        ip = None
        if vlan['id'] == int(settings["CONFIG"]["static-route-next-hop"]):
            ip = vlan["applianceIp"]
            break

    # #### CHECK WITH JAS FIX ME
    if ip is None:
        ip = vlans[0]["applianceIp"]

    if not summary_only:
        subnet = "{}/22".format(lower)   # lower
        name = "lower summary subnet"
        static_route.add_static_route(settings["netid"], name, subnet, ip)

        subnet = "{}/22".format(upper)   # lower
        name = "upper summary subnet"
        static_route.add_static_route(settings["netid"], name, subnet, ip)

    if nnetx_summary:
        subnet = "{}/22".format(nnetx_summary)   # lower
        name = "non-netx-summary"
        static_route.add_static_route(settings["netid"], name, subnet, ip)

if __name__ == "__main__":
    pass
