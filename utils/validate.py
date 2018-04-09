#!/usr/bin/env python3
import json
import csv
import utils.auto_logger as llog
import traceback
import utils.auto_utils as utils
from utils._json import Json
from jsonschema import validate

from jsonschema import validate
from jsonschema import ValidationError, SchemaError


import os



class Csv(object):
    def __init__(self):
        fname_schema = "schema.json"

    @classmethod
    def to_json(self, fname, path="data", absolute_path=None):
        self.item = {}
        if absolute_path:
            fname_csv = "{}/{}.csv".format(absolute_path, fname)
            fname_json = "{}/{}.json".format(absolute_path, fname)
        else:
            fname_csv = utils.get_path(fname, path, "csv")
        entries = []
        try:
            with open(fname_csv, newline='') as csv_file:
                reader = csv.DictReader(csv_file, skipinitialspace=True)
                for entry in reader:
                    entries.append(entry)
                    item = entry.get("syslogEnabled")
                    if item:
                        if item.lower() == "false":
                            entry["syslogEnabled"] = False
                        elif item.lower() == "true":
                            entry["syslogEnabled"] = True
                    #self.Schema.validate(entry)
            if absolute_path:
                Json().writer_full_path(fname_json, entries)
            else:
                Json().writer(fname, entries, path)
        except Exception as err:
            print("fname: {} not found".format(fname))
            #traceback.print_tb(err.__traceback__)
            exit(-1)
        return entries


    def to_json_and_validate(self, fname, input_path=None, output_path=None):
        self.item = {}
        fname_csv = "{}/{}.csv".format(input_path, fname)
        fname_json = "{}/{}.json".format(output_path, fname)
        entries = []


        with open(fname_csv, newline='') as csv_file:
            reader = csv.DictReader(csv_file, skipinitialspace=True)
            for entry in reader:
                item = entry.get("syslogEnabled")
                if item:
                    if item.lower() == "false":
                        entry["syslogEnabled"] = False
                    elif item.lower() == "true":
                        entry["syslogEnabled"] = True
                    import copy
                    entry_validation = copy.deepcopy(entry)

                    schema = {
                        "type": "object",
                        "properties": {
                            "comment": {"type": "string"},
                            "policy": {"enum": ["allow","deny"]},
                            "protocol": {"enum": ["udp", "tcp","any","icmp","Any"]},   # Validate JAS ANY
                            "srcPort" : {"type": "string"},
                            "srcCidr": {"type": "string"},
                            "destPort": {"type": "string"},
                            "destCidr": {"type": "string"},
                            "syslogEnabled": {"type": "boolean"}
                        }
                    }

                    try:
                        validate(entry_validation, schema)
                    except:
                        print ("NOT FIREWALL")

                    # Elimiitae \n chars from string fields
                    for field in ["srcCidr","destCidr","comment","srcPort","destPort"]:
                        entry[field] = entry[field].replace("\n", "")

                    entry["protocol"].replace("Any", "any")
                    # Schema Validatation
                    isL3FwFile = False

                    # if entry_validation.get("srcPort").isnumeric() == False:
                    #      assert (entry_validation["srcPort"]=="Any")
                    # if entry_validation.get("destPort").isnumeric() == False:
                    #       print (entry_validation["destPort"])

                    # Validate Fields are the same and same order
                    schema_keys = list(schema["properties"].keys())
                    item_keys = list(entry.keys())
                    result = [i for i, j in zip(schema_keys, item_keys) if i != j]
                    if len(result) != 0:
                        print ("Mismatch schema keys: {}", schema_keys)
                        print ("Mismatch item   keys: {}", item_keys)

                    assert(len(result)==0)
                    entries.append(entry)

        Json().writer_full_path(fname_json, entries)

            # print("fname: {} not found".format(fname))
            # traceback.print_tb(err.__traceback__)
            #os._exit(-1)
        return entries

    @classmethod
    def write_lines(self, csvfile, field_names, json_data):
        writer = csv.DictWriter(csvfile, field_names)
        writer.writeheader()
        if type(json_data) is list:
            for rowDict in json_data:
                writer.writerow(rowDict)
        else:
            writer.writerow(json_data)

    @classmethod
    def to_csv(self, fname, header=None, path="data"):
        fname_csv = utils.get_path(fname, path, 'csv')
        # reading the Dictionary
        obj = Json()
        json_data = obj.reader(fname, path)
        if type(json_data) == list:
            fieldNames = [k for k, _ in json_data[0].items()]
        else:
            fieldNames = [k for k, _ in json_data.items()]

        fieldNames.sort()
        if header is not None:
            headerOkay=True
            for column in header:
                if column not in fieldNames:
                    headerOkay=False
                    l.logger.error("header column: {} not found".format(column))
                    exit(-1)
            if headerOkay is False:
                return
            # This will make it use the order provided
            fieldNames=header
        try:
            import os
            if os.name == 'nt' :
                with open(fname_csv, 'w', newline='') as csvfile:
                    self.write_lines(csvfile, fieldNames, json_data)
            else:
                with open(fname_csv, 'w') as csvfile:
                    self.write_lines(csvfile, fieldNames, json_data)

        except Exception as err:
            l.logger.error("fname:{} {}".format(fname, fname_csv))
            traceback.print_tb(err.__traceback__)
            assert(0)

def transform_to_json(fname):
    obj=Csv()
    ref = obj.to_json(fname)
    return ref


def transform_to_csv(fname, header=None, path="data"):
    obj=Csv()
    obj.to_csv(fname, header, path)

# Todo move json and csv to proper store_<name subdirectory.
# send ipython to Jas

if __name__ == '__main__':
    import utils.auto_globals as ag
    ag.folder_time_stamp = '../data/cli-deploy-s2svpnrules/AutomationTestOrg_DONOTDELETE/2018_03_24_11_59_54/'
    fname = 's2svpnrules_deploy'
    transform_to_csv(fname, header=None, path="ORG")

    pass

    # transform_to_csv("test_vlans")
    # transform_to_csv("vlans_netx")
    #
    # header=["networkId", "name", "id", "applianceIp", "subnet", "dnsNameservers", "fixedIpAssignments", "reservedIpRanges" ]
    # transform_to_csv("vlans_generated_1234", header)

    # transform_to_csv("vlans_funnel_subnet")
    # transform_to_json("vlans_funnel_subnet")
    #obj = Schema()
    #obj.validation([])



