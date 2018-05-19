# https://raw.githubusercontent.com/meraki/dashboard-api-python/master/meraki.py

import api.meraki as meraki
import json
import utils.auto_logger as l
import global_vars as gv
from utils.auto_pmdb import settings
from utils.auto_logger import logger, runlogs_logger
"""
This module contains custom returnhandler for meraki.

They are required in order to provide :
    - better logging and error handling (__returnhandler_custom)
    - a dummy handler that will always succeed so that script
    testing does not require the meraki api calls to always succeed.
    
"""

"""
This is the handler that is in use and is essentially a copy of the 
meraki api handler but contains logging using our logging module
and also error handling that returns a tuple (Success and Result)
so that handling is error handler is possible at the script level.

This is needed to be able to log meraki api problems and log them.


"""

import utils.auto_globals as auto_globals


def __returnhandler_custom(statuscode, _returntext, objtype, suppressprint):
    """

    Args:
        statuscode: HTTP Status Code
        returntext: JSON String
        objtype: Type of object that operation was performed on (i.e. SSID, Network, Org, etc)
        suppressprint: Suppress any print output when function is called

    Returns:
        errmsg: If returntext JSON contains {'errors'} element
        returntext: If no error element, returns returntext

    """

    validreturn = meraki.__isjson(_returntext)
    noerr = False
    errmesg = ''


    if validreturn:
        returntext = json.loads(_returntext)

        try:
            errmesg = returntext['errors']
        except KeyError:
            noerr = True
        except TypeError:
            noerr = True

    try:
        __returntext = _returntext.replace(",", "\n")
    except:
        pass
    if str(statuscode) == '200' and validreturn:
        logger.info('{0} Operation Successful - See returned data for results\n'.format(str(objtype)))
        logger.debug(_returntext)
        return (True, returntext)
    elif str(statuscode) == '200':
        _str='{0} Operation Successful\n'.format(str(objtype))
        logger.info(_str)
        logger.debug(_returntext)
        return (True, None)
    elif str(statuscode) == '201' and validreturn:
        _str='{0} Added Successfully - See returned data for results\n'.format(str(objtype))
        logger.info(_str)
        logger.debug(_returntext)
        return (True, returntext)
    elif str(statuscode) == '201':
        _str='{0} Added Successfully\n'.format(str(objtype))
        logger.info(_str)
        logger.debug(_returntext)
        return (True, returntext)
    elif str(statuscode) == '204' and validreturn:
        _str='{0} Deleted Successfully - See returned data for results\n'.format(str(objtype))
        logger.info(_str)
        logger.debug(_returntext)
        return (True, returntext)
    elif str(statuscode) == '204':
        _str = '{0} Deleted Successfully\n'.format(str(objtype))
        logger.info(_str)
        logger.debug(_returntext)
        return (True, None)
    elif str(statuscode) == '400' and validreturn and noerr is False:
        runlogs_logger.error('Bad Request - See returned data for error details\n')
        runlogs_logger.error(__returntext)
        logger.error('Bad Request - See returned data for error details\n')
        logger.error(__returntext)
        return (False, __returntext)
    elif str(statuscode) == '400' and validreturn and noerr:
        runlogs_logger.error('Bad Request - See returned data for details\n')
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('Bad Request - See returned data for details\n')
        logger.error('Returned data:\n{}'.format(__returntext))
        return (False, __returntext)
    elif str(statuscode) == '400':
        runlogs_logger.error('Bad Request - No additional error data available\n')
        logger.error('Bad Request - No additional error data available\n')
    elif str(statuscode) == '401' and validreturn and noerr is False:
        runlogs_logger.error('Unauthorized Access - See returned data for error details\n')
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('Unauthorized Access - See returned data for error details\n')
        logger.error('Returned data:\n{}'.format(__returntext))
        return (False, __returntext)
    elif str(statuscode) == '401' and validreturn:
        runlogs_logger.error('Unauthorized Access')
        logger.error('Unauthorized Access')
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('Returned data:\n{}'.format(__returntext))
        return (False, __returntext)
    elif str(statuscode) == '404' and validreturn and noerr is False:
        runlogs_logger.error('Resource Not Found - See returned data for error details\n')
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('Resource Not Found - See returned data for error details\n')
        logger.error('Returned data:\n{}'.format(__returntext))
        return (False, errmesg)
    elif str(statuscode) == '404' and validreturn:
        runlogs_logger.error('Resource Not Found')
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('Resource Not Found')
        logger.error('Returned data:\n{}'.format(__returntext))
        return (False, __returntext)
    elif str(statuscode) == '500':
        runlogs_logger.error('HTTP 500 - Server Error')
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('HTTP 500 - Server Error')
        logger.error('Returned data:\n{}'.format(__returntext))
        return (False, __returntext)
    elif validreturn and noerr is False:
        runlogs_logger.error('HTTP Status Code: {0} - See returned data for error details\n'.format(str(statuscode)))
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('HTTP Status Code: {0} - See returned data for error details\n'.format(str(statuscode)))
        logger.error('Returned data:\n{}'.format(__returntext))
        return False, errmesg
    else:
        runlogs_logger.error('HTTP Status Code: {0} - No returned data (possibly BAD API_KEY)\n'.format(str(statuscode)))
        runlogs_logger.error('Returned data:\n{}'.format(__returntext))
        logger.error('HTTP Status Code: {0} - No returned data (possible invalid API_KEY)\n'.format(str(statuscode)))
        logger.error('Returned data:\n{}'.format(__returntext))
        return (False, _returntext)

def __returnhandler_custom_dummy_run(statuscode, returntext, objtype, suppressprint):
    return True, None


def adddevtonet(apikey, networkid, serial, suppressprint=False):
    return True, None


def claim(apikey, orgid, serial=None, licensekey=None, licensemode=None, orderid=None, suppressprint=False):
    return True, None


def removedevfromnet(apikey, networkid, serial, suppressprint=False):
    return True, None


def updatemxl3fwrules(apikey, networkid, fwrules, syslogDefaultRule=False, suppressprint=False):
    return True, None


def getmxl3fwrules(apikey, networkid, suppressprint=False):
    return True, None


def getnetworklist(apikey, orgid, templateid=None, suppressprint=False):
    return True, None


def getnetworkdetail(apikey, networkid, suppressprint=False):
    return True, None


def updatenetwork(apikey, networkid, name, tz, tags, suppressprint=False):
    return True, None


def addnetwork(apikey, orgid, name, nettype, tags, tz, cloneid=None, suppressprint=False):
    return True, None


def delnetwork(apikey, networkid, suppressprint=False):
    return True, None


def addvlan(apikey, networkid, vlanid, name, subnet, mxip, suppressprint=False):
    return True, None


def addstaticroute(apikey, networkid, name, subnet, ip, suppressprint=False):
    return True, None


def updatevlan(apikey, networkid, vlanid, name=None, subnet=None, mxip=None, fixedipassignments=None, reservedipranges=None, vpnnatsubnet=None, dnsnameservers=None, suppressprint=False):
    return True, None

def getmxvpnfwrules(apikey, orgid, suppressprint=False):
    return True, None

def getvlans(apikey, networkid, suppressprint=False):
    return True, None

def delvlan(apikey, networkid, vlanid, suppressprint=False):
    return True, None

def updatevpnsettings(apikey, networkid, mode='none', subnets=None, usevpn=None, hubnetworks=None, defaultroute=None,
                      suppressprint=False):
    return True, None

def updatemxvpnfwrules(apikey, orgid, vpnrules, syslogDefaultRule=False, suppressprint=False):
    return True, None

"""
This are the monkey patch that is called (see call below, when the module is
imported).

 For normal runs only patching thre return handler is required
 For dryruns we need to patch all used meraki call but the network list,
 which is used to find out the netid for the store. (This is read-only so
 has no impact on the network or scripts other than the small one-off delay for
 the script.
   

"""


def set_run():
        meraki.__returnhandler = __returnhandler_custom


def set_dry_run():
        meraki.__returnhandler = __returnhandler_custom
        meraki.adddevtonet = adddevtonet
        meraki.claim = claim
        meraki.removedevfromnet = removedevfromnet
        meraki.updatemxl3fwrules = updatemxl3fwrules
        meraki.getmxl3fwrules = getmxl3fwrules
        #meraki.getnetworklist = getnetworklist
        meraki.getnetworkdetail = getnetworkdetail
        meraki.updatenetwork = updatenetwork
        meraki.addnetwork = addnetwork
        meraki.delnetwork = delnetwork
        meraki.addvlan = addvlan
        meraki.addstaticroute = addstaticroute
        meraki.updatevlan = updatevlan
        meraki.getvlans = getvlans
        meraki.delvlan = delvlan
        meraki.getmxvpnfwrules= getmxvpnfwrules
        meraki.updatevpnsettings = updatevpnsettings
        meraki.updatemxvpnfwrules = updatemxvpnfwrules

"""

This is the monkey patch in order to always return true.
This patch is called soon after the auto_globals.setStoreName call
(The set storeName needs to retrieve all the stores for the network so
only after that we want to return dummy calls.

This call is enabled by an environment variable that resides in 
the auto_logger so that this can be hot-configured.

"""
def init_meraki_patch():
    if settings.get("dry-run"):
        set_dry_run()
    else:
        set_run()

init_meraki_patch()
