#!/usr/bin/env python3
import utils.auto_json as json
import utils.auto_logger as log
import api.static_route as static_route
import automation.vlan_handler as vlan_handler
from utils.auto_pmdb import settings
import utils.auto_json as mkjson
from api.vlans import get_vlan


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
    pos_lan = int(settings["CONFIG"]["static-route-next-hop"])
    for vlan in vlans:
        ip = None
        if vlan['id'] == pos_lan:
            ip = vlan["applianceIp"]
            break

    # if the pos lan is not in the list
    # we have to look it up on Meraki
    if ip is None:
        # First get details on all vlans
        netid = settings["netid"]
        vlan_pos = get_vlan(netid, pos_lan)
        ip = vlan_pos["applianceIp"]

    if not summary_only:
        subnet = "{}/22".format(lower)   # lower
        name = "lower summary subnet"
        static_route.add_route(settings["netid"], name, subnet, ip)

        subnet = "{}/22".format(upper)   # lower
        name = "upper summary subnet"
        static_route.add_route(settings["netid"], name, subnet, ip)

    if nnetx_summary:
        subnet = "{}/22".format(nnetx_summary)   # lower
        name = "non-netx summary subnet"
        static_route.add_route(settings["netid"], name, subnet, ip)

def find_route(routes, name_to_del):
    for route in routes:
        name = route["name"]
        if name == name_to_del:
            route_id = route["id"]
            return route_id
    log.logger.error("route to delete with name '{}' not found.".format(name_to_del))
    log.runlogs_logger.error("route to delete with name '{}' not found.".format(name_to_del))
    return None

def del_route(netid, name):
    routes = static_route.get_routes(netid)
    #str = mkjson.make_pretty(routes)
    route_id = find_route(routes, name)
    if route_id :
        static_route.del_route(netid, route_id)
        log.logger.info("deleted static-route : {}". format(name, route_id))
        log.runlogs_logger.info("deleted static-route : {}". format(name, route_id))


from utils.auto_globals import load_store, load_org
from api.meraki_patch import init_meraki_patch
def del_route_test():
    init_meraki_patch()
    _orchestration_agent = "cli-test"
    org_name = "AutomationTestOrg_DONOTDELETE"
    load_org(_orchestration_agent, org_name)
    load_store("agent-secret", "8501")

    netid = settings["netid"]

    del_route(netid, "non-netx summary subnet" )

if __name__ == "__main__":
    pass
