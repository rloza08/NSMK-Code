#!/usr/bin/env python3
import utils.auto_logger as l
import utils.auto_json as json
import api.devices as devices
import automation.vlan_handler as vlan_handler
import utils.auto_config  as config
from copy import deepcopy
import utils.auto_utils as utils
import  utils._csv as Csv
# from  utils._json import Json
import utils.auto_globals as auto_globals
import automation.bulk_update as bulk
import api.firewall as firewall
import global_vars as gv

"""
Inputs: 
    firewall_template,
           {
        "comment": "1755",
        "destCidr": "VLAN(70).19",
        "destPort": "22",
        "policy": "allow",
        "protocol": "tcp",
        "srcCidr": "VLAN(24).23",

....
      
    vlan_funnel_table	
{
    "1": "10.218.28.16/27",
    "14": "10.218.28.248/29",
    "16": "10.218.29.0/24",
    "19": "10.218.30.0/24",
    "24": "10.218.31.0/24",
    "35": "10.154.28.0/27",
    
....
    
    output:
        firewall_converted.json
        
    {
        "comment": "413",
        "destCidr": "10.154.28.126/32",
        "destPort": "58019",
        "policy": "allow",
        "protocol": "tcp",
        "srcCidr": "10.218.31.23/32",
        "srcPort": "Any",
        "syslogEnabled": false
    },
    
    
"""
class FirewallHandler(object):
    def __init__(self, _fw_rules=None):
        self.vlanFunnelTable = vlan_handler.createVlanTable()
        fname = _fw_rules
        self.firewallOutputFile = "l3fwrules_deploy_{}".format(auto_globals.store_number)
        self.firewallOutputFileNetx = "l3fwrules_netx"

        #self.header_netx_csv = ["policy", "protocol", "srcCidr", "srcPort", "destCidr", "destPort", "comment", "syslogEnabled"]
        self.header_netx_csv =  ["comment", "policy", "protocol", "srcPort", "srcCidr", "destPort", "destCidr", "syslogEnabled"]


        self.fwRules = json.reader(fname, "templates")
        self.funnelNetx = json.reader("vlans_funnel_netx")
        assert(self.funnelNetx)

        # Transform template to csv for external use
        Csv.transform_to_csv(fname, header=self.header_netx_csv, path="templates")

        # Transform template to  format for external use
        self.transform_rules_from_vlan_to_netx()


        if self.fwRules  is None:
            l.logger.error("unable to load rules from firewall_template : {}". format(fname))
        l.logger.info("using firewall golden rule : {}".format(fname))

    """
        Transforms a single firewall rule.

        Input:
            rule
                'VLAN(70).62'
                ===> vlanid = 70
                     offset = 62

            from the vlan_funnel_table (for the store) for vlanid 70 we get
                     '10.154.28.64/26'

                     oct4 = 64 (from above) + offset (62)
                     oct4 = 126

        Output: new rule

                ===> 10.154.28.126/32  (always /32)

        """

    def vlans_to_netx(self, rule):
        vlans = rule.split(",")
        subnets = []
        for vlan in vlans:
            if vlan.find("VLAN") < 0:
                subnet = vlan
            else:
                vlan = vlan.replace("(", ",")
                vlan = vlan.replace(")", ",")
                vlanList = vlan.split(",")
                if len(vlanList) < 2:
                    l.logger.error(vlanList)
                    assert (0)
                vnumber = vlanList[1]
                """
                Obtain the offset to be added to create the 4th octet
                """
                offset = vlanList[2]
                offset = offset.replace(".", "")

                success, value = utils.get_key_value_in_data(json_data = self.funnelNetx, keyField="Vlan", valueField="Subnet", match=vnumber)
                if success is False:
                    l.logger.debug("vlan:{} not found in vlans_funnel_netx.json file".format(vnumber))
                    return None

                if int(vnumber) >= 990:
                    netx_val = "NET{}".format(vnumber)
                else:
                    convert = {'a': 'NETA', 'b' : 'NETB' , 'c': 'NETC', 'd':'NETD',
                               'e': 'NETE', 'f': 'NETF', 'g' : 'NETG', 'h':'NETH'}
                    value = value.split('.')[0]
                    netx_val = convert.get(value)

                assert(netx_val)
                subnet = "{}.{}".format(netx_val, offset)
            subnets.append(subnet)
        ref = ", ".join(subnets)
        return ref


    def transform_rules_from_vlan_to_netx(self):
        """
        Transforms all the firewall rules
        """
        # Using deep copy to avoid future stepping into fw references.
        rules = deepcopy(self.fwRules)
        for rule in rules:
            rule["destCidr"] = self.vlans_to_netx(rule["destCidr"])
            rule["srcCidr"] = self.vlans_to_netx(rule["srcCidr"])
            if rule["policy"] == "allow":
                rule["policy"] = "permit"

        #json.writer(self.firewallOutputFileNetx, rules, header=self.header_netx_csv, path="templates")
        l.logger.debug("created {}".format(self.firewallOutputFileNetx))

    """
    Transforms a single firewall rule.
    
    Input:
        rule
            'VLAN(70).62'
            ===> vlanid = 70
                 offset = 62
            
        from the vlan_funnel_table (for the store) for vlanid 70 we get
                 '10.154.28.64/26'
                 
                 oct4 = 64 (from above) + offset (62)
                 oct4 = 126
                 
    Output: new rule
    
            ===> 10.154.28.126/32  (always /32)
        
    """
    def vlans_to_subnet(self, rule):
        vlans = rule.split(",")
        subnets = []
        for vlan in vlans:
            if vlan.find("VLAN") < 0:
                subnet = vlan
            else:
                vlan = vlan.replace("(", ",")
                vlan = vlan.replace(")", ",")
                vlanList = vlan.split(",")
                if len(vlanList) < 2:
                    l.logger.error(vlanList)
                    assert (0)
                vnumber = vlanList[1]
                """
                Obtain the offset to be added to create the 4th octet
                """
                offset = vlanList[2]
                offset = offset.replace(".", "")

                lookup = self.vlanFunnelTable.get(vnumber)

                if lookup is None:
                    l.logger.error("vlan:{} not found in table".format(vnumber))
                    return None

                if offset == "*":
                    subnet = lookup
                else :
                    """
                    Octect 4 is obtained by using the vlan table 4th octect
                    and adding the offset obtained from the step above.
                    """
                    _subnet = lookup.split(".")
                    offset=int(offset)
                    octect4 = int(_subnet[3].split("/")[0])
                    octect4 = octect4+offset
                    if (octect4>255):
                        assert(octect4<=255)
                    subnet = "{}.{}.{}.{}/32".format(_subnet[0],_subnet[1],_subnet[2], octect4)
            subnets.append(subnet)
        ref = ",".join(subnets)
        return ref


    def transform_rules_from_vlan_to_subnet(self):
        """
        Transforms all the firewall rules
        """
        # Using deep copy to avoid future stepping into fw references.
        self.fwNewRules = deepcopy(self.fwRules)
        for rule in self.fwNewRules:
            rule["destCidr"] = self.vlans_to_subnet(rule["destCidr"])
            rule["srcCidr"] = self.vlans_to_subnet(rule["srcCidr"])
            """
            Syslog enabled is breaking the api so we force it to disabled.
            """
            rule["syslogEnabled"] = False

        rules=[]
        """
        Don't apply default rules
        """
        for rule in self.fwNewRules:
            if rule["comment"] == "Default rule":
                continue
            rules.append(rule)
        json.writer(self.firewallOutputFile, rules)
        self.fwRules=deepcopy(rules)
        l.logger.debug("created {}".format(self.firewallOutputFile))

"""
Remove the serials 
Not in use.
"""
def remove_serials():
    # Convert meraki template firewall to subnet firewall
    fname = "firewall_serials"
    data = Csv.transform_to_json(fname)
    json.writer(fname, data[0])
    for item in range(len(data)):
        netid = data[item]["id"]
        serial1 = data[item]["serial1"]
        serial2 = data[item]["serial2"]
        devices.removedevice(netid, serial1)
        devices.removedevice(netid, serial2)
    # Does physical VLAN creation on meraki device
    l.logger.info("success")


"""
Using the /templates/firewall_template
"""
def convert(fw_rules=None):
    obj = FirewallHandler(fw_rules)
    # "Source": "VLAN(19).21" to "Source": "167.146.66.21"
    # obj.convertFwRulesToJson(fw_input)
    # Actual Conversion of firewall rules based on VlanTable
    obj.transform_rules_from_vlan_to_subnet()

def deploy(agent, fw_rules=None):
    # Convert meraki template firewall to subnet firewall
    convert(fw_rules)
    # Does physical VLAN creation on meraki device

    netid = auto_globals.netid
    store_number = auto_globals.store_number
    firewall._set(netid, fw_rules, store_number)
    l.runlogs_logger.info("l3fwrules deployed netid:{}".format(netid))
    l.logger.info("successfully deployed netid:{}".format(netid))

def get(agent):

    netid = auto_globals.netid
    store_number = auto_globals.store_number
    firewall._get(netid, store_number)
    l.runlogs_logger.info("got l3fwrules for netid:{}".format(netid))
    l.logger.info("got l3fwrules for  netid:{}".format(netid))


def bulk_update(agent):
    l.runlogs_logger.info("bulk get started")

    if agent is "cli-deploy-networks":
        org_group = auto_globals.deploy_l3fwrules_org
        fw_rules = auto_globals.deploy_l3fwrules_version
        store_list = auto_globals.deploy_l3fwrules_store_list
    else:
        org_group = auto_globals.l3fwrules_org
        fw_rules = auto_globals.l3fwrules_version
        store_list = auto_globals.l3fwrules_store_list

    org_list = json.reader(org_group,"templates")

    for org in org_list:
        org_name = org["org_name"]
        l.runlogs_logger.info("selected org: {}".format(org_name))
        l.runlogs_logger.info("using l3fwrules : {}".format(fw_rules))
        auto_globals.select_org(org_name)
        fw_rules = "{}".format(auto_globals.l3fwrules_version)
        bulk.perform_bulk_update_firewall(agent, deploy, org_name, fw_rules, store_list)
    l.runlogs_logger.info("bulk get finished")

def bulk_update_get(agent):
    l.runlogs_logger.info("bulk update get started")

    org_group = auto_globals.l3fwrules_org
    store_list = auto_globals.l3fwrules_store_list

    org_list = json.reader(org_group,"templates")

    for org in org_list:
        org_name = org["org_name"]
        l.runlogs_logger.info("selected org: {}".format(org_name))
        auto_globals.select_org(org_name)
        bulk.perform_bulk_get_firewall(agent, get, org_name, store_list)
    l.runlogs_logger.info("bulk update finished")



if __name__ == '__main__':
    store_list = "Store-List-SHA"
    org_group="New_Production_MX_Org"
    bulk_update(agent="firewall_update_bulk", org_group=org_group, fw_rules=None, store_list=store_list)
