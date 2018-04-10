#!/usr/bin/env python3
import utils.auto_json as json
import utils.auto_logger as l
import utils.auto_config as config
import api.static_route as static_route
import automation.vlan_handler as vlan_handler
import api.network  as network
import utils.auto_globals  as auto_globals


def add():
	"""
	Adds upper and lower static routes

	Inputs:
		upper subnet
		lower subnet
		vlans_generate_<netid> file

	Outputs:


		add via /api/static_route (lower_subnet, ip)
		add via /api/static_route (upper_subnet, ip)

	"""
	fname, lower, upper = vlan_handler.createVlanFiles()
	l.logger.debug(fname)

	# Get the ip from the vlans_generated file
	vlans = json.reader(fname.split(".")[0])
	for vlan in vlans:
		ip=None
		if vlan['id'] == int(config.static_route_next_hop):
			ip = vlan["applianceIp"]
			break

	subnet= "{}/22".format(lower)   # lower
	name="lower summary subnet"
	static_route.add_static_route(auto_globals.netid, name, subnet, ip)

	subnet= "{}/22".format(upper)   # lower
	name="upper summary subnet"
	static_route.add_static_route(auto_globals.netid, name, subnet, ip)

if __name__ == "__main__":
	auto_globals.setStoreName("SHAWS_9611")
	add()
