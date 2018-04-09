#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_logger as l
import api.meraki as meraki
import traceback
import api.network as networks

"""
This call provides a wrapper to the meraki add static route

"""


class StaticRoute(object):
	@classmethod
	def add(self, netid, name, subnet, ip):
		success = False
		str = None
		try:
			success, str = meraki.addstaticroute(config.api_key, netid, name, subnet, ip)
			if not success:
				l.logger.error("{}".format(str))
				assert(0)
		except Exception as err:
			l.logger.error("exception failure netid:{}".format(netid))
			traceback.print_tb(err.__traceback__)
			assert (0)
		return success, str


def add_static_route(netid, name, subnet, ip):
	StaticRoute.add(netid, name, subnet, ip)


if __name__ == '__main__':
	pass
