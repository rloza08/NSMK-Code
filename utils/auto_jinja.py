#!/usr/bin/env python3
import os
import utils.auto_json as Json
import utils.auto_logger as l
from jinja2 import Environment, FileSystemLoader
import traceback
import utils.auto_utils as utils
import utils._csv as csv_json
import json

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
	autoescape=False,
	loader=FileSystemLoader(os.path.join(PATH, '../config')),
	trim_blocks=False)


class JinjaAutomation(object):
	@classmethod
	def render_template(self, template_filename, context):
		str = None
		try:
			str = TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
		except Exception as err:
			l.logger.error("template_filename:{}".format(template_filename))
			traceback.print_tb(err.__traceback__)
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


if __name__ == "__main__":
	netid=77777
	template="vlans_set_template.json"
	output="vlans_generated_{}".format(netid)
	context = create_test_context()
	l.logger.debug(context)
	obj = JinjaAutomation()
	obj.create_output(template, output, context)


"""	
ISSUES:
inja2.exceptions.UndefinedError: dict object has no element 18

added dummy entry to funnel_vlans_table.json

"""