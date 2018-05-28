#!/usr/bin/env python3
import utils.auto_json as json
import utils.auto_logger as l
import utils.auto_jinja as auto_jinja
import api.vlans as vlans
import api.netx as netx
from utils.auto_config import json_reader, make_pretty
from utils._json import Json

import os
from utils.auto_globals import CONFIG_DIR, RUNTIME_DIR, TEMPLATES_DIR
from utils.auto_pmdb import settings
from copy import deepcopy


"""
This module contains two classes:

i)  vlanTable    - vlan table creation based on funnel and item

ii) vlanHandler  - vlan_generated_<netid> generation using jinja

                (based on vlan_table and /templates/vlans_set_template.json
                
        The jinja context (data to be applied to the template) is obtained from vlans_table
        The template is used as is from /templates/vlan_set_template.json

Also contains a deploy function which
1) call the two classes above
2) calls the low level api to create/update the vlans.

        
"""

"""
This class is used to obtain a 

output: vlans_funnel_table.json
{
    "1": "10.218.28.16/27",
    "14": "10.218.28.248/29",
    "16": "10.218.29.0/24",
    "19": "10.218.30.0/24",
...

from 

a) vlans_funnel.csv
    Vlan,Subnet,Description
    1,10.x.a.16/27,Network Management
    4,10.x.a.32/27,Network Management
    ....

b) vlans_netx.json (obtained by calling /api/item.py)
{
    "a": "10.218.28",
    "b": "10.218.29",
    "c": "10.218.30",
    "d": "10.218.31",
    "e": "10.154.28",
    ...
"""
"""

"""

class VlanTemplates(object):

    def load_funnel_and_patch(self):
        vlans_funnel_base_file = "vlans-funnel-base"
        vlans_patch_file = "vlans-patch"
        vlans_funnel_base = json_reader("{}/{}.json".format(RUNTIME_DIR, vlans_funnel_base_file))
        vlans_patch = json_reader("{}/{}.json".format(TEMPLATES_DIR, vlans_patch_file))
        return vlans_funnel_base, vlans_patch


    def upgrade_funnel(self, vlans_add_flag=False):
        if vlans_add_flag:
            vlans_funnel_base = []
            vlans_patch = settings["vlans-add-list"]
        else:
            vlans_funnel_base, vlans_patch = self.load_funnel_and_patch()

        vlans_funnel_file = "vlans-funnel"

        # Throw away all vlans that don't have a subnet (used only for template generation)
        entries = []
        for vlan in vlans_patch:
            entry = {}
            if vlan["Subnet"] == "":
                continue
            entry["Vlan"] = vlan["Vlan"]
            entry["Subnet"] = vlan["Subnet"]
            entry["Description"] = vlan["Description"]  # not used but copied for clarity
            item = deepcopy(entry)
            entries.append(item)

        vlans_funnel = vlans_funnel_base + entries
        Json.writer(vlans_funnel_file, vlans_funnel, path=RUNTIME_DIR, absolute_path=True)

    # Basic fields come from augmented Men and Mice
    def add_basic_fields(self, entry, vlan):
        vlan_id = int(vlan['Vlan'])
        o4 = vlan['Subnet'].split('.')
        o4 = o4[3]
        o4 = o4.split("/")
        o4 = int(o4[0])
        entry["id"] = deepcopy(vlan_id)
        entry["networkId"] = "{{networkid}}"
        desc = vlan['Description']
        # Cleans up non-supported chars that Meraki does not like
        for ch in [".", "@", "#", "_", "-", '"', "]", "}", ")", "(", "[", "{"]:
            desc = desc.replace(ch, " ")

        entry["name"] = desc
        entry["applianceIp"] = "{{{{vlan[{}]['octets']}}}}.{}".format(vlan_id, o4 + 1)
        subnet = vlan["Subnet"]
        if subnet.find("10.x") >= 0:
            entry["subnet"] = "{{{{vlan[{}]['subnet']}}}}".format(vlan_id)
        else:
            entry["subnet"] = subnet

        entry["fixedIpAssignments"] = {}
        entry["reservedIpRanges"] = []


    def add_extended_fields(self, entry, vlan_patch=None):
        if vlan_patch == None:
            entry["dnsNameservers"] = "upstream_dns"
            entry["reservedIpRanges"] = []
            return
        entry["dnsNameservers"] = vlan_patch["dnsNameservers"]
        entry["reservedIpRanges"] = []
        if vlan_patch["reservedIpRanges1-comment"] != "":
            item = dict()
            id = vlan_patch["Vlan"]
            item["comment"] = vlan_patch["reservedIpRanges1-comment"]

            aux = "{}".format(vlan_patch["reservedIpRanges1-end"])
            tpl_str = "{{{{vlan[{}]['octets']}}}}.{}".format(id, aux)
            item["end"] = tpl_str

            aux = "{}".format(vlan_patch["reservedIpRanges1-start"])
            tpl_str = "{{{{vlan[{}]['octets']}}}}.{}".format(id, aux)
            item["start"] = tpl_str

            entry["reservedIpRanges"].append(deepcopy(item))

        if vlan_patch["reservedIpRanges2-comment"] != "":
            item = dict()
            id = vlan_patch["Vlan"]
            item["comment"] = vlan_patch["reservedIpRanges2-comment"]

            aux = "{}".format(vlan_patch["reservedIpRanges2-end"])
            tpl_str = "{{{{vlan[{}]['octets']}}}}.{}".format(id, aux)
            item["end"] = tpl_str

            aux = "{}".format(vlan_patch["reservedIpRanges2-start"])
            tpl_str = "{{{{vlan[{}]['octets']}}}}.{}".format(id, aux)
            item["start"] = tpl_str

            entry["reservedIpRanges"].append(deepcopy(item))


    def build_jinja_template(self, vlans_add_flag=False):
        if vlans_add_flag:
            vlans_funnel = settings['vlans-add-list']
            vlans_patch = settings['vlans-add-list']
        else:
            vlans_funnel_file = "vlans-funnel"
            vlans_patch_file = "vlans-patch"

            vlans_funnel = json_reader("{}/{}.json".format(RUNTIME_DIR, vlans_funnel_file))
            vlans_patch = json_reader("{}/{}.json".format(TEMPLATES_DIR, vlans_patch_file))

        # Create patch lookup table
        patch_table = {}
        for vlan in vlans_patch:
            id = vlan["Vlan"]
            patch_table[id] = vlan

        # Merge and create jinja template
        entries = []
        for vlan in vlans_funnel:
            entry = dict()
            self.add_basic_fields(entry, vlan)
            vlan_patch = patch_table.get(vlan["Vlan"])
            if vlan_patch != None:
                self.add_extended_fields(entry, vlan_patch)
            else:
                self.add_extended_fields(entry)

            item = deepcopy(entry)
            entries.append(item)

        jinja_template = entries
        Json.writer("jinja_vlans_template", jinja_template, path="runtime")
        return jinja_template


class VlanTable(object):
    def __init__(self):
        obj = VlanTemplates()
        # Creates a new full that has been patched
        vlans_add_flag = (settings["agent"] == "cli-deploy-vlans-add")
        obj.upgrade_funnel(vlans_add_flag)
        obj.build_jinja_template(vlans_add_flag)

        self.funnel_file = settings["CONFIG"]["funnel-file"]

    """
    From vlans_funnel.csv (obtained from men and mice)
    Generates all the intermediate and the final
    vlans_funnel_table.json (using for vlans generation)
    
    Uses item info (from vlans_netx.json to convert to the proper store subnet)
    """

    def create(self):
        # Get item for the shop and saves it into the netx_file
        self.create_vlan_defs()
        self.convert_funnel_to_json()

        # Making men and mice format more consistent with item format
        # Changes from 10.x.a.96/27 to a.96/27
        self.transform_funnel_to_netx()

        # Turning funnel (men and mice) into actual shop-subnet info.
        # from g.0/25 to 167.146.68.19
        # generates funnel_vlans_subnet
        self.transform_funnel_to_subnet()

        # creates  "95": "167.146.70"
        self.create_funnel_vlan_table()
        return self.funnel_vlan_table

    """
     Process :
        queries /api/item.py and saves it into /data/../vlans_netx.json
    """

    def create_vlan_defs(self):
        self.netx = netx.Netx()
        self.valid_subnets = self.netx.valid_subnet_list
        self.netxFile = settings["CONFIG"]["netx-file"]
        device = "{}{}{}".format(settings["CONFIG"]["device-prefix"], settings["store-number"], settings["CONFIG"]["device-postfix"])
        self.netx = self.netx.get_netx(device)
        json.writer(self.netxFile, self.netx)
        l.logger.debug("created {}".format(self.netxFile))

    """
    Transforms the vlans_funnel.csv into vlans_funnels.json format
    """

    def convert_funnel_to_json(self):
        self.funnel = Json.reader(self.funnel_file, "runtime")
        self.funnelNetxFile = "{}_netx".format(self.funnel_file)
        self.funnel_subnet_file = "{}_subnet".format(self.funnel_file)
        self.funnelVlanFile = "{}_table".format(self.funnel_file)
        return self.funnel

    """
    Changes the format from 10.x.a.96/27 to a.96/27
    and creates vlan_funnel_netx.json from vlans_funnel.json
    """

    def transform_funnel_to_netx(self):
        for entry in self.funnel:
            subnet = entry["Subnet"].split(".")
            # if there is an x than we need to replace otherwise skip
            if subnet[1] == 'x':
                if (subnet[2] >= 'a' and subnet[2] <= 'z'):
                    entry["Subnet"] = subnet[2] + "." + subnet[3]
        json.writer(self.funnelNetxFile, self.funnel)
        l.logger.debug("created {}".format(self.funnelNetxFile))

    """
    Inputs:
     vlans_funnel_netx.json
     vlans_netx.json
     
    Outputs:
     vlans_funnel_subnet.json
     
     
    Transforms from the format g.0/25 to 167.146.68.19 to a.96/27
    Looks up the subnet from item and replaces in the vlans_funnel_netx.json
    and creates  
    
        from vlans_funnel_netx.json

        {
            "Description": "Network Management",
            "Subnet": "a.16/27",
            "Vlan": "1"
        },


        vlan_funnel_subnet.json

        {
        "Description": "Network Management",
        "Subnet": "10.218.28.16/27",
        "Vlan": "1"
        },
    
    """

    def transform_funnel_to_subnet(self):
        for entry in self.funnel:
            subnet = entry["Subnet"].split(".")
            netxIndex = subnet[0]
            if netxIndex in self.valid_subnets:
                subnet[0] = self.netx[netxIndex]
                elem = entry["Subnet"].split(".")
                entry["Subnet"] = "{}.{}".format(subnet[0], elem[1])
                json.writer(self.funnel_subnet_file, self.funnel)
        l.logger.debug("created {}".format(self.funnel_subnet_file))

    """
    From a vlan_funnel_subnet.json format
            {
                "Description": "Network Management",
                "Subnet": "10.218.28.16/27",
                "Vlan": "1"
            },
    
    Create a vlan_funnel_table.json which is more appropriate or lookups
        {
            "1": "10.218.28.16/27",
            "14": "10.218.28.248/29",
            "16": "10.218.29.0/24",
            "19": "10.218.30.0/24",

    
    """

    # Table of Vlan to convert
    def create_funnel_vlan_table(self):
        self.funnel_vlan_table = {}
        for entry in self.funnel:
            vlan = entry["Vlan"]
            self.funnel_vlan_table[vlan] = entry["Subnet"]

        json.writer(self.funnelVlanFile, self.funnel_vlan_table)
        l.logger.debug("created {}".format(self.funnelVlanFile))


"""
Vlan generation using jinja
"""
class VlanHandler(object):
    def __init__(self, template, output):
        self.template = template
        self.output = output
        self.netid = settings["netid"]

    def __init__(self):
        self.template = None
        self.output = None
        self.netid = settings["netid"]

    """
    Process:
     Creates a context (json structure) used
     by jinja in conjuction with a template to generate a file
     
     Reads the vlans_funnel and loads into a table by vlanid:
     which contains:
      a) Three octets
      b) the full funnel subnet.
      
    Inputs:
      i) vlans_funnel (obtained from men and mice)
      
    
    """

    def create_context(self):
        self.context = {
            'networkid': None,
            'vlan': {}
        }

        self.context['networkid'] = self.netid
        fname = "{}_table".format(settings["CONFIG"]["funnel-file"])
        vlans = json.reader(fname)

        for key, value in vlans.items():
            vlanId = int(key)
            subnet = value
            octets = subnet.split(".")
            octets = "{}.{}.{}".format(octets[0], octets[1], octets[2])
            """
            Sample usage inside the template.
            (note vlan is only a name to lock the reference with the template,
            could not be anything)
                'applianceIp': "{{vlan[19]['octets']}}.1",
            """
            self.context["vlan"][vlanId] = {}
            self.context["vlan"][vlanId]['octets'] = octets
            self.context["vlan"][vlanId]['subnet'] = subnet
        l.logger.debug(self.context)

    """
        From the context created below: 
        (which contains the octects and subnets 
         for each vlan-id)
        
        self.context["vlan"][vlanId] = {}
        self.context["vlan"][vlanId]['octets'] = octets
        self.context["vlan"][vlanId]['subnet'] = subnet
    
        And using the /templates/vlans_set_template below:
        
        "applianceIp": "{{vlan[19]['octets']}}.1",
        "dnsNameservers": "upstream_dns",
        "fixedIpAssignments": {},
        "id": 19,
        "name": "generalstorelan",
        "networkId": "{{networkid}}",
        "reservedIpRanges": [],
        "subnet": "{{vlan[19]['subnet']}}"
        
        And using Jinja apply the context to the template and obtain
        the vlans_generated_<netid>
        
        {
            "applianceIp": "10.218.30.1",
            "dnsNameservers": "upstream_dns",
            "fixedIpAssignments": {},
            "id": 19,
            "name": "generalstorelan",
            "networkId": "N_686798943174004623",
            "reservedIpRanges": [],
            "subnet": "10.218.30.0/24"
        },
    
    """

    def create_vlan_generated(self):
        # Obtain a jinja handler hook
        obj = auto_jinja.JinjaAutomation()
        # Creates the final vlans_generated_<netid>
        obj.create_output(self.template, self.output, self.context)

    def create_vlan_table(self):
        self.vlan_table = VlanTable()
        ref = self.vlan_table.create()
        return ref

    """
    Creates all required files for vlan setup
    and most importantly the vlans_generated_<netid> file
    
    Inputs:
     i) vlans_set_template.json (VLAN (meraki VLAN style) templated file. 
     ii) vlans_netx.json (contains item info generated for this particular store
     
    Outputs:
     i) vlans_generated_<netid>.json (used to call meraki api and create/update the vlans.
     
    Obs: This module uses jinja2 template to produce the final file.
    """

    def create_vlan_files(self):
        self.create_vlan_table()
        # Create/Update for all VLANs
        self.netid = settings["netid"]
        self.template = "jinja_vlans_template.json"
        self.output = "vlans_generated_{}".format(settings["netid"])
        # Creates vlan table with three octets/subnet
        self.create_context()
        # Using jinja apply the above context to the vlan_template
        self.create_vlan_generated()
        return self.output


def createVlanTable():
    obj = VlanHandler()
    ref = obj.create_vlan_table()
    return ref


def createVlanFiles():
    obj = VlanHandler()
    ref = obj.create_vlan_files()
    lower = obj.vlan_table.netx["lower"]
    upper = obj.vlan_table.netx["upper"]
    return ref, lower, upper


def deploy_new():

    obj = VlanHandler()
    """
        This simply creates all the intermediate files and the final
        vlan_generated_<netid> file which is used to call
        the meraki api and create/update vlans for this network.
    """
    obj.create_vlan_files()

    # Does physical VLAN creation on meraki device by callin the /api/vlan module
    netid = settings["netid"]
    vlans.create_update_vlans(netid)


def deploy():
    obj = VlanHandler()
    """
        This simply creates all the intermediate files and the final
        vlan_generated_<netid> file which is used to call
        the meraki api and create/update vlans for this network.
    """
    obj.create_vlan_files()

    # Does physical VLAN creation on meraki device by callin the /api/vlan module
    netid = settings["netid"]
    vlans.update_vlans(netid)


def vlans_delete(netid, vlans_list):
    for vlan in vlans_list:
        vlanid = vlan["Vlan"]
        vlans.delete(netid, vlanid)



if __name__ == "__main__":
    pass
