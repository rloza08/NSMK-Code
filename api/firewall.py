#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_json as json
import utils.auto_logger as l
from api.meraki_patch import meraki
import traceback
import global_vars as gv

class Firewall(object):
    """
    This allows to test each rule , good for finding bugs in the rules
    """
    @classmethod
    def _set_each(self, netid):
        success=False
        str=None
        try:
            fname = config.firewall_converted
            fwrules = json.reader(fname)
            singleRule = []
            for rule in fwrules:
                singleRule.append(rule)
                success, str = meraki.updatemxl3fwrules(config.api_key, netid, singleRule)
                l.logger.debug(rule["comment"])
            if not success:
                l.logger.error("failed rule comment:{} {}".format(rule["comment"], str))
                gv.fake_assert()
        except Exception as err:
            l.logger.error("exception failure netid:{}".format(netid))
            traceback.print_tb(err.__traceback__)
            gv.fake_assert()
        return success, str

    """

    Wrapper to meraki api that applies firewall rules
    from a given file name (normally firewall_converted_<netid>.json
    
    """
    @classmethod
    def set(self, netid, fw_rules):
        success=False
        str=None
        try:
            fwrules = json.reader("l3fwrules_meraki_api")
            success, str = meraki.updatemxl3fwrules(config.api_key, netid, fwrules)
            if not success:
                l.logger.error("failed netid:{} {}".format(netid, str))
                assert (0)
        except Exception as err:
            l.logger.error("exception failure netid:{}".format(netid))
            traceback.print_tb(err.__traceback__)
            assert (0)
        return success, str


    """
    
    Wrapper to meraki api to get firewall rules
    from a given netid (normally firewall_converted_<netid>.json
    
    Input:
        netid of firewall
        
    Output:
        firewall_<netid>.json
    
    ps. Not in use.
    """
    def get(self, netid):
        self.firewalls = None
        try:
            success, self.firewalls = meraki.getmxl3fwrules(config.api_key, netid)
            if not success:
                l.logger.error("failed netid:{} {}".format(netid, self.firewalls))
            fname = "l3fwrules_get_{}".format(netid)
            json.writer(fname, self.firewalls)
        except Exception as err:
            l.logger.error("exception failure netid:{}".format(netid))
            traceback.print_tb(err.__traceback__)
            gv.fake_assert()


def _get(netid):
    """Gets firewall rules for a given netid into a json file"""
    obj = Firewall()
    obj.get(netid)


def _set(netid, fw_rules=None):
    """Sets the firewall from a json file"""
    obj = Firewall()
    obj.set(netid, fw_rules)


def set_each(netid):
    """Sets the firewall from a json file"""
    obj = Firewall()
    obj._set_each(netid)

if __name__ == '__main__':
    obj=Firewall()
    networkid = "L_686798943174001160"

    #obj.get(networkid)
    success, str= obj.set(networkid)
