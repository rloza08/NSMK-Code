#!/usr/bin/env python3
from api.meraki_patch import meraki
import utils.auto_config as config
import utils.auto_logger as l
import utils.auto_globals as auto_globals
import utils.auto_json as Json
import global_vars as gv
from utils.auto_pmdb import settings

class VpnFirewall(object):
        @classmethod
        def update_settings_single(self, org_id, vpn_rules=[]):
            api_key = config.api_key
            success = False
            str = None
            try:
                single_rule = []
                count = 1100
                start=count
                for rule in vpn_rules[start:]:
                    l.runlogs_logger.info("deploying rule number: {} ==>  rule: {}".format(count, str))
                    single_rule.append(rule)
                    success, str = meraki.updatemxvpnfwrules(api_key, org_id, single_rule,
                                                         syslogDefaultRule=False,
                                                         suppressprint=False)
                    single_rule.pop()
                    count +=1
                    str = Json.make_pretty(rule)
                    l.logger.info("deployed org-id {} count {} rule number {}".format(org_id, count, str))
                    l.runlogs_logger.info("deployed org-di {} rule number {}".format(org_id, count))
                    Json.writer("s2svpnrules_deploy", single_rule)

                    if not success:
                        l.logger.error("failed count {} {}".format(count, str))
                        l.runlogs_logger.error("failed count {}  {}".format(count, str))
                        l.runlogs_logger.error("{}".format(str))
                        gv.fake_assert()
            except Exception as err:
                l.runlogs_logger.error("org_id: {} str:{}".format(org_id, str))
                l.logger.error("org_id: {} str:{}".format(org_id, str))
                gv.fake_assert()
            return success, str

        def update_settings(self, org_id, vpn_rules=[]):
            api_key = config.api_key
            try:
                success, str = meraki.updatemxvpnfwrules(api_key, org_id, vpn_rules,
                                                         syslogDefaultRule=False,
                                                         suppressprint=False)

                l.logger.info("updatemxvpnfwrules {} {}".format(success, str))
                import json as _json
                aux = _json.dumps(str)[0:160]
                Json.writer("s2svpnrules_deploy", vpn_rules, path="ORG")
                l.runlogs_logger.info("updatemxvpnfwrules {}".format(success))
                l.logger.debug("updatemxvpnfwrules {} {}".format(success, str))

                if success:
                    return True, None

                if success:
                    l.logger.info("success org-id {}".format(org_id))
                    l.runlogs_logger.info("success  org-id {}".format(org_id))
                    Json.writer("vpn_updatevpnfwrules_{}".format(org_id), str)
                else:
                    l.logger.error("failed org-id {} {}".format(org_id, str))
                    l.runlogs_logger.error("failed  org-id {} {}".format(org_id, aux))
                    gv.fake_assert()
            except Exception as err:
                l.logger.error("{}".format(str))
                l.logger.error("exception failure org_id: {}".format(org_id))
                l.runlogs_logger.error("{}".format(str))
                l.runlogs_logger.error("exception failure org_id: {}".format(org_id))
                gv.fake_assert()
            return success, str

        def get_settings(self, org_id):
            api_key = config.api_key
            vpn_rules_str = ""
            success=False
            try:
                success, vpn_rules = meraki.getmxvpnfwrules(api_key, org_id)
                if success:
                    l.logger.debug("success")
                    Json.writer("s2svpnrules_get", vpn_rules, path="ORG", header=None, logPath=True)
                else:
                    l.runlogs_logger.error("failed: {}".format(str))
                    l.logger.error("failed: {}".format(str))
                    gv.fake_assert()
            except Exception as err:
                l.logger.error("org_id: {} str:{}".format(org_id, str))
                l.runlogs_logger.error("org_id: {} str:{}".format(org_id, str))
                gv.fake_assert()
            return success, str

"""
Sets the vpn firewall from a json file for a given orgid
"""
def _set(org_name, fw_rules=None):
    org_id = settings["org-id"]
    assert(fw_rules)
    fname = fw_rules

    _vpn_rules = Json.reader(fname, "templates")
    vpn_rules = []
    # Remove default rules
    for entry in _vpn_rules:
        if entry.get("comment") == "Default rule":
            continue
        vpn_rules.append(entry)
    obj = VpnFirewall()
    obj.update_settings(org_id, vpn_rules)

"""
Sets the vpn firewall from a json file for a given orgid
"""
def _get(org_name):
    org_id = auto_globals.get_orgid(org_name)
    from utils.auto_json import Json
    obj = VpnFirewall()
    obj.get_settings(org_id)


if __name__ == '__main__':
    org_name = "New_Production_MX_Org"
    _set(org_name)

