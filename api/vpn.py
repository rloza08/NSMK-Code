#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_json as json
import utils.auto_logger as l
import api.meraki as meraki
import global_vars as gv

# success, str = meraki.getmxvpnfwrules(config.api_key, utils.orgid)
# str = json.make_pretty(str)
# l.logger.info("{} {}".format(success, str))

# def updatemxvpnfwrules(api_key, orgid, vpnrules, syslogDefaultRule=False, suppressprint=False):


class Vpn(object):
	@classmethod
	def update_settings(self, networkid, hubnetworks, defaultroute, subnets, usevpn):
		success = False
		str = None
		try:
			mode = 'spoke'
			success, str = meraki.updatevpnsettings(config.api_key, networkid, mode,
                                                    subnets, usevpn, hubnetworks, defaultroute)
			if success:
				l.logger.debug("success netid {}")
				json.writer("vpn_updatevpnsettings_{}".format(networkid), str)
			else:
				l.logger.error("failure netid {} {}".format(networkid, str))
				l.runlogs_logger.error("{}".format(str))
				gv.fake_assert()
		except  Exception as err:
			l.logger.error("exception failure networkid: {} str:{}".format(networkid, str))
			l.runlogs_logger.error("exception failure str:{}".format(str))
			gv.fake_assert()
		return success, str



""""
	hubnetworks = 

"""


def updatevpnsettings(networkid, hubnetworks, defaultroute, subnets, usevpn):
	usevpn = [True, True]
	obj = Vpn()
	obj.update_settings(networkid, hubnetworks, defaultroute, subnets, usevpn)


if __name__ == '__main__':
	hubnetworks = ["N_686798943174001360"]
	defaultroute = [True]
	subnets = ["10.235.88.0/22", "10.171.88.0/22"]
	usevpn = [True, True]
	updatevpnsettings("Test_Store_1234", hubnetworks, defaultroute, subnets, usevpn)

