#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_json as json
import utils.auto_logger as log
from api.meraki_patch import meraki
import global_vars as gv

class Firewall(object):
    """
    This allows to test each rule , good for finding bugs in the rules
    """
    @classmethod
    def set_each(self, netid, fw_rules, store_number):
        success=False
        str=None
        try:
            fwrules = json.reader("l3fwrules_deploy_{}".format(store_number))
            singleRule = []
            for rule in fwrules:
                singleRule.append(rule)
                success, str = meraki.updatemxl3fwrules(config.api_key, netid, singleRule)
                log.logger.debug(rule["comment"])
            if not success:
                log.logger.error("failed rule comment:{} {}".format(rule["comment"], str))
                log.runlogs_logger.error("failed rule comment:{} {}".format(rule["comment"], str))
                gv.fake_assert()

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            log.logger.error("Meraki error: {}".format(err.default))
            log.runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)

        except Exception as err:
                log.logger.error("exception failure netid:{} {}".format(netid, str))
                log.runlogs_logger.error("exception failure netid:{}".format(str))
                gv.fake_assert()
        return success, str

    """

    Wrapper to meraki api that applies firewall rules
    from a given file name (normally firewall_converted_<netid>.json
    
    """
    @classmethod
    def set(self, netid, fw_rules, store_number):
        success=False
        str=None
        try:
            fwrules = json.reader("l3fwrules_deploy_{}".format(store_number))
            success, str = meraki.updatemxl3fwrules(config.api_key, netid, fwrules)
            log.logger.info("success netid {} {}".format(netid, str))
            if not success:
                log.logger.error("failed netid {} {}".format(netid, str))
                log.runlogs_logger.error("failed {} {}".format(netid, str))
                gv.fake_assert()
        except Exception as err:
            log.logger.error("exception failure netid {}\n{}".format(netid, str))
            log.runlogs_logger.error("exception failure netid {}\n{}".format(netid, str))
            gv.fake_assert()
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
    def get(self, netid, store_number):
        self.firewalls = None
        try:
            success, self.firewalls = meraki.getmxl3fwrules(config.api_key, netid)
            if not success:
                log.logger.error("failed netid {} {}".format(netid, self.firewalls))
                log.runlogs_logger.error("failed netid {}".format(netid, self.firewalls))
                gv.fake_assert()
            fname = "l3fwrules_get_{}".format(store_number)

            json.writer(fname, data=self.firewalls, path="data", header=None, logPath=True)
        except Exception as err:
            log.logger.error("exception failure {} netid {}\n{}".format(err, netid, self.firewalls))
            log.runlogs_logger.error("exception {} failure netid \n{}".format(err, self.firewalls))
            gv.fake_assert()

def _get(netid, store_number):
    """Gets firewall rules for a given netid into a json file"""
    obj = Firewall()
    obj.get(netid, store_number)

def _set(netid, fw_rules=None, store_number=None):
    """Sets the firewall from a json file"""
    obj = Firewall()
    obj.set(netid, fw_rules, store_number)


def _set_each(netid, fw_rules=None, store_number=None):
    """Sets the firewall from a json file"""
    obj = Firewall()
    obj.set_each(netid, fw_rules, store_number)

if __name__ == '__main__':
    obj=Firewall()
    networkid = "L_686798943174001160"

    #obj.get(networkid)
    success, str= obj.set(networkid)
