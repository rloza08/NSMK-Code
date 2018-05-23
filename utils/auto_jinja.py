#!/usr/bin/env python3
import os
import utils.auto_json as Json
import utils.auto_logger as l
from jinja2 import Environment, FileSystemLoader
import utils.auto_utils as utils
import utils.low_csv as csv_json
import json
import global_vars as gv
from utils.auto_globals import RUNTIME_DIR
PATH1 = os.path.dirname(os.path.abspath(__file__))
PATH2 = os.path.join(PATH1, RUNTIME_DIR)

TEMPLATE_ENVIRONMENT = Environment(
	autoescape=False,
	loader=FileSystemLoader(PATH2),
	trim_blocks=False)


class JinjaAutomation(object):
	@classmethod
	def render_template(self, template_filename, context):
		str = None
		try:
			str = TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
		except Exception as err:
			l.logger.error("template_filename:{} {}".format(template_filename, err))
			l.runlogs_logger.error("template_filename:{} {}".format(template_filename, err))
			gv.fake_assert()
			os._exit(-1)

		result = json.loads(str)
		return result

	def create_output(self, template, fname, context):
		data = self.render_template(template, context)
		if data is None:
			l.logger.error("failed")
			return
		csv_json.Json().writer(fname, data)
		header=["id", "networkId", "name",  "applianceIp", "subnet", "dnsNameservers", "fixedIpAssignments", "reservedIpRanges" ]
		csv_json.transform_to_csv(fname, header)
		# csv_json.transform_to_json(fname)
		l.logger.debug(fname)

	def _create_output(self, template, fname, context):
		fname_json = utils.get_path(fname, path="data", extension="json")
		with open(fname_json, 'w') as f:
			output = self.render_template(template, context)
			if output is None:
				l.logger.error("failed")
				return
			f.write(output)
			l.logger.debug(fname_json)

"""
Context used only for testing
"""
def create_test_context():
	context = {
		'networkid': "L_650207196201623673",
		'vlan' : {}
	}

	fname = "vlans_funnel_table"
	vlans = Json.reader(fname)

	for key, value in vlans.items():
		vlanId = int(key)
		subnet=value
		octets=subnet.split(".")
		octets="{}.{}.{}".format(octets[0], octets[1], octets[2])
		context["vlan"][vlanId] = {}
		context["vlan"][vlanId]['octets'] = octets
		context["vlan"][vlanId]['subnet'] = subnet
	return context

def convert_master_template_to_jinja():
	from utils.auto_json import reader, make_pretty
	from copy import deepcopy
	master_tpl = reader("vlan_template_master_final", configDir="config")
	# str = make_pretty(master_tpl)
	# print(str)
	jinja_tpl=[]
	item={}
	for vlan in master_tpl:
		id=vlan["Vlan"]
		item["id"]=id

		item["networkId"]="{{networkid}}"
		item["name"]=vlan["Description"]

		subnet = vlan["Subnet"]
		last_cctect = subnet.split(".")
		last_octect = last_cctect[3]
		last_octect = last_cctect[3].split("/")
		last_octect = int(last_octect[0])
		str = "{{vlan[{}]['subnet']}}.{}".format(id, last_octect+1)
		item["applianceIp"]= str

		subnet = vlan["Subnet"]
		str = "{{vlan[{}]['subnet']}}".format(id)
		item["subnet"]=str

		item["dnsNameservers"] = vlan["dnsNameservers"]
		item["fixedIpAssignments"]= {}
		item["reservedIpRanges"] = []

		if vlan["reservedIpRanges1-start"] is not "":
			it = {}
			it["comment"]=vlan["reservedIpRanges1-comment"]
			it["end"] =vlan["reservedIpRanges1-end"]
			it["start"]=vlan["reservedIpRanges1-start"]
			item["reservedIpRanges"].append(deepcopy(it))

		if vlan["reservedIpRanges2-start"] is not "":
			it = {}
			it["comment"]=vlan["reservedIpRanges2-comment"]
			it["end"] =vlan["reservedIpRanges2-end"]
			it["start"]=vlan["reservedIpRanges2-start"]
			item["reservedIpRanges"].append(deepcopy(it))

		jinja_tpl.append(deepcopy(item))


	str = make_pretty(jinja_tpl)
	print(str)

if __name__ == "__main__":
	# netid=77777
	# template="vlans_set_template.json"
	# output="vlans_generated_{}".format(netid)
	# context = create_test_context()
	# l.logger.debug(context)
	# obj = JinjaAutomation()
	# obj.create_output(template, output, context)
	convert_master_template_to_jinja()

"""	
ISSUES:
inja2.exceptions.UndefinedError: dict object has no element 18

added dummy entry to funnel_vlans_table.json

"""