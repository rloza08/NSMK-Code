#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_json as json
from api.meraki_patch import meraki
import global_vars as gv
from utils.auto_pmdb import settings
from utils.auto_logger import logger, runlogs_logger

"""
This module encapsulates the meraki device api calls.

It can be used separately by calling the module entry points
or importing the module and using the class.

Example:

Runs the test code ./devices.py

 
"""
class Devices(object):

    def update_device(self, networkid=None, serial=None, name=None):
        success = False
        str = None
        try:
            success, str = meraki.updatedevice(config.api_key, networkid, serial, name, tags=None, lat=None, lng=None, address=None, move=None, suppressprint=False)
            if success:
                logger.info("success {}".format(networkid))
                #json.writer("addtonet_{}".format(serial), str)
            else:
                runlogs_logger.error("updatedevice failed networkid: {} serial:{}".format(networkid, serial))
                logger.error("updatedevice failed networkid: {} serial:{}".format(networkid, serial))

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            runlogs_logger.info("updatedevice name success")
            logger.info("updatedevice success networkid {} serial{}".format(networkid, serial))
            exit(-1)
        except Exception as err:
            runlogs_logger.error("updatedevice failed {} networkid: {} serial:{}".format(err, networkid, serial))
            logger.error("updatedevice failed {} networkid: {} serial:{}".format(err, networkid, serial))
            gv.fake_assert()
        return success, str


    def addtonet(self, networkid, serial):
        success = False
        try:
            success, _str = meraki.adddevtonet(config.api_key, networkid, serial)
            if success:
                logger.debug("success {}".format(networkid))
                json.writer("addtonet {}".format(serial), _str)
            else:
                logger.error("failed.")
                logger.error("{}".format(str))

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            logger.error("failed {}".format(err.default))
            runlogs_logger.error("failed {}".format(err.default))
            exit(-1)
        except Exception as err:
            runlogs_logger.error("failed {} serial:{}".format(err, serial))
            logger.error("failed {} networkid: {} serial:{}".format(err, networkid, serial))
            gv.fake_assert()
        return success, _str

    def claim(self, serial, licensekey=None, licensemode=None, orderid=None):
        success = False
        str=None
        try:
            success, self.claim = meraki.claim(config.api_key, settings["org-id"],
                                               serial, licensekey,
                                               licensemode, orderid)
            if not success:
                runlogs_logger.error("orgid: {} serial:{} claim:{}".format(settings["org-id"], serial, self.claim))
                logger.error("orgid: {} serial:{} claim:{}".format(settings["org-id"], serial, self.claim))
                return False

            #json.writer("claim_{}".format(serial), self.claim)

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            logger.error("orgid: {} Meraki error: {}".format(settings["org-id"], err.default))
            runlogs_logger.error("orgid: {}  Meraki error: {}".format(settings["org-id"], err.default))
            exit(-1)
        except Exception as err:
            logger.error("serial:{}".format(serial))
            runlogs_logger.error("serial:{}".format(serial))
            gv.fake_assert()

        return success

"""
Converts the network-serials-v?.csv to json
Using the cli on settings networks add networks-serials entry
Deploy networks now calls deploy_claim
Looks 
"""
def deploy_serials():
    networkid = settings["netid"]
    serial = settings["serial"]
    device_name = settings["device-name"]
    """Creates a networks and returns a network id"""
    obj=Devices()
    # Claims the serial from inventory to the org-id
    success = obj.claim(serial)
    if not success:
        return False
    # Adds the device to the networkid
    success = obj.addtonet(networkid, serial)
    if not success:
        return False
    # Updates the device_name to the device
    # update just to update the device name
    success = obj.update_device(networkid, serial, name=device_name)
    return success


def removedevice(networkid, serial):
    try:
        meraki.removedevfromnet(config.api_key, networkid, serial)
    except (meraki.EmailFormatError,
            meraki.OrgPermissionError,
            meraki.ListError) as err:
        logger.error("Meraki error: {}".format(err.default))
        runlogs_logger.error("Meraki error: {}".format(err.default))
        exit(-1)

def bulkremove(fname):
    from utils.low_json import Json
    items = Json.reader("bulk_remove")
    for item in items:
        netid = item["netid"]
        serial = item["serial"]
        meraki.removedevfromnet(config.api_key, netid, serial)

if __name__ == '__main__':
	pass
