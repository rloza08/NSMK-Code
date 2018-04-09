#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_json as json
import utils.auto_logger as l
from api.meraki_patch import meraki
import traceback
import utils.auto_globals as auto_globals

"""
This module encapsulates the meraki device api calls.

It can be used separately by calling the module entry points
or importing the module and using the class.

Example:

Runs the test code ./devices.py

 
"""
class devices(object):
	def addtonet(self, networkid, serial):
		success = False
		str = None
		try:
			success, str = meraki.adddevtonet(config.api_key, networkid, serial)
			if success:
				l.logger.debug("success")
				json.writer("addtonet_{}".format(serial), str)
			else:
				l.logger.error("failed.")
				l.logger.error("{}".format(str))
		except  Exception as err:
			l.logger.error("networkid: {} serial:{}".format(networkid, serial))
			traceback.print_tb(err.__traceback__)
		return success, str

	def claim(self, serial, licensekey=None, licensemode=None, orderid=None):
		success = False
		str=None
		try:
			success, self.claim = meraki.claim(config.api_key, auto_globals.orgid,
                                               serial, licensekey,
                                               licensemode, orderid)
			if not success:
				l.logger.error("orgid: {} serial:{} claim:{}".format(orgid, serial, self.claim))
				json.writer("claim_{}".format(serial), self.claim)
			json.writer("claim_{}".format(serial), self.claim)
		except Exception as err:
			l.logger.error("serial:{}".format(serial))
			traceback.print_tb(err.__traceback__)

		return success, self.claim
"""
Not in Use
"""
def claimadd(networkid, serial):
	"""Creates a networks and returns a network id"""
	obj=devices()
	success, str = obj.claim(serial)
	if success:
		obj.addtonet(networkid, serial)

def removedevice(networkid, serial):
	meraki.removedevfromnet(config.api_key, networkid, serial)

def bulkremove(fname):
	from utils._json import Json
	items = Json.reader("bulk_remove")
	for item in items:
		netid = item["netid"]
		serial = item["serial"]
		meraki.removedevfromnet(config.api_key, netid, serial)


if __name__ == '__main__':
	"""
	Please change serial number and network id and remove the
	exit(0) in order to run a :
	- claimadd 
	- removeddevice
	"""
	exit(0)
	serial="Q2PN-KRED-QSMA"
	networkid = "N_686798943174003816"
	claimadd(networkid, serial)
	removedevice(networkid, serial)
