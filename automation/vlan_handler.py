#!/usr/bin/env python3
import utils.auto_json as json
import utils.auto_logger as l
import utils.auto_jinja as auto_jinja
import api.vlans as vlans
import utils.auto_config as config
import api.netx as netx
import utils._csv as Csv
import utils.auto_globals as auto_globals
from utils.auto_globals import CONFIG_DIR, vlans_add_list
from utils.auto_config import json_reader, make_pretty
from copy import deepcopy
from utils._json import Json
import shutil
import os
from utils.auto_csv import convert_to_json

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

class VlanTable(object):
    def __init__(self):
        self.funnel_file = config.vlan_funnel_file

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
        self.netxFile = config.netx_file
        device="{}{}{}".format(config.device_prefix, auto_globals.store_number, config.device_postfix)
        self.netx = self.netx.get_netx(device)
        json.writer(self.netxFile, self.netx)
        l.logger.debug("created {}".format(self.netxFile))


    """
    Transforms the vlans_funnel.csv into vlans_funnels.json format
    """
    def convert_funnel_to_json(self):
        self.funnel=Csv.transform_to_json((self.funnel_file), "config")
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
            if subnet[1]=='x':
                if (subnet[2]>='a' and subnet[2]<='h'):
                    entry["Subnet"]=subnet[2]+"."+subnet[3]
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
                elem=entry["Subnet"].split(".")
                entry["Subnet"] = "{}.{}".format(subnet[0],elem[1])
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
        self.funnel_vlan_table={}
        for entry in self.funnel:
            vlan = entry["Vlan"]
            self.funnel_vlan_table[vlan]=entry["Subnet"]

        json.writer(self.funnelVlanFile, self.funnel_vlan_table)
        l.logger.debug("created {}".format(self.funnelVlanFile))

"""
Vlan generation using jinja
"""
class VlanHandler(object):
    def __init__(self, template, output):
        self.template = template
        self.output = output
        self.netid = auto_globals.netid

    def __init__(self):
        self.template = None
        self.output = None
        self.netid = auto_globals.netid

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
            'vlan' : {}
        }

        self.context['networkid']=self.netid
        fname = "{}_table".format(config.vlan_funnel_file)
        vlans = json.reader(fname)

        for key, value in vlans.items():
            vlanId = int(key)
            subnet=value
            octets=subnet.split(".")
            octets="{}.{}.{}".format(octets[0], octets[1], octets[2])
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
        self.vlan_table=VlanTable()
        ref=self.vlan_table.create()
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
        self.netid = auto_globals.netid
        self.template="jinja_vlans_template.json"
        self.output="vlans_generated_{}".format(auto_globals.netid)
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
    netid = auto_globals.netid
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
    netid = auto_globals.netid
    vlans.update_vlans(netid)

def add_entry_to_template(t_new, vlan):
    vlan_id = int(vlan['Vlan'])
    o4 = vlan['Subnet'].split('.')
    o4 = o4[3]
    o4 = o4.split("/")
    o4 = int(o4[0])
    entry = {}
    entry["id"] = vlan_id
    entry["networkId"] =  "{{networkid}}"
    entry["name"] =  vlan['Description']
    entry["applianceIp"] =  "{{{{vlan[{}]['octets']}}}}.{}".format(vlan_id, o4+1)
    entry["subnet"] =  "{{{{vlan[{}]['subnet']}}}}".format(vlan_id)
    entry["dnsNameservers"] =  "upstream_dns"
    entry["fixedIpAssignments"] =  {}
    entry["reservedIpRanges"] =  []
    t_new.append(entry)



def ENTER_ENV_vlan_add():
    #import os
    cwd = os.getcwd()
    try:
        from utils._csv import read_remove_csv_header
        csv_fname = "{}/../../templates/{}.csv".format(cwd, vlans_add_list)
        csv_fname_append = "{}/../../templates/{}_append.csv".format(cwd, vlans_add_list)
        vlans_add_list_contents = read_remove_csv_header(csv_fname, csv_fname_append)

        # Backup the funnel file
        src = "{}/../config/vlans_funnel.csv".format(cwd)
        dst = "{}/../config/vlans_funnel_orig.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        destination.close()

        src = "{}/../menAndMice/funnel.csv".format(cwd)
        dst = "{}/../config/vlans_funnel.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)

        # 99x Vlan patch that is always used
        patch_01 = "{}/../config/vlans_funnel.patch.csv".format(cwd)
        shutil.copyfileobj(open(patch_01, 'rb'), destination)

        # Vlan patch just for this run
        patch_02 = "{}/../../templates/{}_append.csv".format(cwd, vlans_add_list)
        shutil.copyfileobj(open(patch_02, 'rb'), destination)
        destination.close()
        convert_to_json("vlans_funnel", "config",None)
    except:
        l.logger.error("failed")
        assert (0)

    src = "{}/../config/jinja_vlans_template.json".format(cwd)
    dst = "{}/../config/jinja_vlans_template_orig.json".format(cwd)
    destination = open(dst, 'wb')
    shutil.copyfileobj(open(src, 'rb'), destination)
    destination.close()


    update_vlan_template(funnel_file="vlans_funnel",
                             vlans_template_file="jinja_vlans_template",
                             vlans_template_file_previous="jinja_vlans_template_previous",
                             vlans_template_file_new="jinja_vlans_template")

    return vlans_add_list_contents

def LEAVE_ENV_vlan_add():

    # Now restore the men and mice file in config back to
    # its original state
    cwd = os.getcwd()
    try:
        src = "{}/../config/jinja_vlans_template_orig.json".format(cwd)
        dst = "{}/../config/jinja_vlans_template.json".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        destination.close()

        src = "{}/../config/vlans_funnel_orig.csv".format(cwd)
        dst = "{}/../config/vlans_funnel.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        destination.close()
    except:
        l.logger.error("failed")
        assert (0)


def update_vlan_template(funnel_file="vlans_funnel",
                         vlans_template_file="jinja_vlans_template",
                         vlans_template_file_previous="jinja_vlans_template_previous",
                         vlans_template_file_new = "jinja_vlans_template") :

    vlans_new = json_reader("{}/{}.json".format(CONFIG_DIR, funnel_file))
    vlans_template_orig = json_reader("{}/{}.json".format(CONFIG_DIR, vlans_template_file))

    t_old = vlans_template_orig
    t_new = deepcopy(t_old)

    for funnel_vlan in vlans_new:
        found = False
        vlan = int(funnel_vlan['Vlan'])
        # Check with Jas
        if vlan == 1:
            continue
        for item in t_new:
            if int(vlan) == item["id"]:
                found = True
                break

        if not found:
            add_entry_to_template(t_new, funnel_vlan)

    #vlans_new = json_writer(funnel_new_file)
    # create a backup for the existing jinja template
    cwd = os.getcwd()
    src = "{}/{}.json".format(CONFIG_DIR, vlans_template_file)
    dst = "{}/{}.json".format(CONFIG_DIR, vlans_template_file_previous)
    destination = open(dst, 'wb')
    shutil.copyfileobj(open(src, 'rb'), destination)

    Json.writer(vlans_template_file_new, t_new, path="config")

    tpl = make_pretty(t_new)
    return t_new


if __name__ == "__main__":
    # #auto_globals.setStoreName("SHAWS_9611")
    # deploy()
    # #createVlanTable()
    update_vlan_template("../menAndMice/funnel.json",
                                 "../config/jinja_vlans_template.json",
                                 "../runtime/jinja_vlans_template_new.json")
