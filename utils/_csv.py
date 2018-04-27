
#!/usr/bin/env python3
import csv
import utils.auto_logger as l
import utils.auto_utils as utils
from utils._json import Json
from utils.auto_utils import is_numeric, is_numeric_in_range, is_non_zero_number

from jsonschema import validate
import sys
import global_vars as gv

def show_error(str):
    l.logger.error(str)
    sys.stdout.flush()


class Csv(object):
    def __init__(self):
        pass

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
                        if item.lower() == "true":
                            entry["syslogEnabled"] = True
                        else :
                            entry["syslogEnabled"] = False

                    #self.Schema.validate(entry)
            if absolute_path:
                Json().writer_full_path(fname_json, entries)
            else:
                Json().writer(fname, entries, path)
        except Exception as err:
            l.logger.error("fname: {} not found".format(fname))
            l.runlogs_logger.error("fname: {} not found".format(fname))
            gv.EOM()
            gv.fake_assert()
        return entries

    def validate_ip_item(self, comment, line_count, it, field):
        success=False
        if it.find("/") > 0:
            aux = it.split("/")
            four_octets = aux[0]
            mask = aux[1]
            if is_numeric_in_range(mask, 1, 32) is False:
                str = "ref: {}\nline #:{} - invalid mask {}\n{}".format(comment, line_count, it, field)
                l.message_user(str)
                return False
        elif it.find(" mask ") > 0:
            aux = it.split(" mask ")
            four_octets = aux[0]
            mask = aux[1]
            if not self.validate_four_octets(mask):
                str = "ref: {}\nline #:{} - invalid mask {}\n{}".format(comment, line_count, it, field)
                l.message_user(str)
                return False
        elif it == "any":
            return True
        elif it == "":
            str = "ref: {}\nline #:{} - inconsistent mask {}\n,{}".format(comment, line_count, it, field)
            l.message_user(str)
            return False
        else:
            str = "ref: {}\nline #:{} - invalid {}\n,{}".format(comment, line_count, it, field)
            l.message_user(str)
            return False
        if self.validate_four_octets(four_octets) is False:
            return False
        return True

    def validate_vlan_item(self, it):
        if it.find("VLAN(") < 0:
            return False
        else:
            its = it.split(".")
            fourth_octet = its[1]
            if is_non_zero_number(fourth_octet) is False:
                if fourth_octet != "*":
                    return False
            vlan = it.split("(")[1]
            vlan_number = vlan.split(")")[0]
            if is_non_zero_number(vlan_number) is False:
                return False
        return True


    def validate_vlan_and_ip(self, entry, field, line_count):
        item = entry[field]
        items = item.split(",")
        item_count = 0
        for it in items:
            item_count += 1
            if self.validate_vlan_item(it) is False:
                if field == "srcCidr":
                    if it == "any":
                        continue
                    octet = it.split(".")
                    # Upgrade logic with three octets and mask check
                    if octet[0] == "192" and octet[1] == "168":
                        continue
                elif field == "destCidr":
                    comment=entry["comment"]
                    if self.validate_ip_item(comment, line_count, it, field):
                        continue
                str = "line #:{} item:{}- invalid {} item: {}".format(line_count, item_count, field, item)
                l.message_user(str)
                continue

        return True

    def validate_port(self, entry, field, line_count):
        item = entry.get(field)
        items = item.split(",")
        item_count = 0
        for item in items:
            item_count += 1
            # Is it a port range
            if item == "any":
                if len(items)==1:
                    return True
            elif item.find("-") > 0:
                if len(items)==1:
                    range = item.split("-")
                    if len(range) == 2:
                        if is_numeric_in_range(range[0], 1, 65535) and \
                                is_numeric_in_range(range[1], 1, 65535):
                            return True
            else:
                # It has to be a valid port
                if is_numeric_in_range(item, 1, 65535):
                    return True
            str = "line #:{} - invalid {} : {}".format(line_count, field, item)
            l.message_user(str)

        return False

    def validate_four_octets(self, four_octets):
        octets = four_octets.split(".")
        if len(octets) != 4:
            l.message_user(str)
            return False
        # Review if first octect has to be non-zero
        for octet in octets:
            if is_numeric_in_range(octet, 0, 255) is False:
                l.message_user(str)
                return False
        return True


    def validate_ip_range(self, entry, field_name, line_count):
        comment = entry.get("comment")
        field = entry.get(field_name)
        items = field.split(",")
        success = True
        for item in items:
            self.validate_ip_item(comment, line_count, item, field)
        return success

    def to_json_and_validate(self, fname, input_path=None, output_path=None):
        json_data = Json.reader("valid_inputs", path="templates")
        self.schemas = json_data[0]

        self.item = {}
        fname_csv = "{}/{}.csv".format(input_path, fname)
        fname_json = "{}/{}.json".format(output_path, fname)
        entries = []

        # Find schema to use in validation
        file_type=None
        schema = None
        for entry in self.schemas:
            item = self.schemas[entry]
            fname_pattern = item["fname_pattern"]
            if fname.find(fname_pattern) == 0:
                file_type = entry
                schema = item["json_schema"]
                break

        if schema is None:
            print ("No valid schema match\n"
                   "check file name follows correct pattern: {}\n"
                   "Store-List-* / Org-* / l3fwrules_template_ / s2svpnrules_".format(fname))
            gv.EOM()
            gv.fake_assert()

        with open(fname_csv, newline='') as csv_file:
            entries = csv.DictReader(csv_file, skipinitialspace=True)
            line_count = 0
            for entry in entries:
                line_count +=1
                try:
                    validate(entry, schema)
                    # Validate Fields are the same and same order
                    schema_keys = list(schema["properties"].keys())
                    item_keys = list(entry.keys())
                    result = [i for i, j in zip(schema_keys, item_keys) if i != j]
                    if len(result) != 0:
                        print("line #:{} - mismatch schema keys: {}".format(line_count, schema_keys))
                        print("line #:{} - mismatch item   keys: {}".format(line_count, item_keys))
                        gv.EOM()
                        gv.fake_assert()
                except:
                    print ("invalid schema line number :{} \ {}".format(line_count, entry))
                    gv.EOM()
                    gv.fake_assert()

        is_firewall = (file_type=="l3fwrules" or file_type=="s2svpnrules")
        json_data = []

        line_count = 0
        with open(fname_csv, newline='') as csv_file:
            line_count +=1
            entries = csv.DictReader(csv_file, skipinitialspace=True)
            if is_firewall is False:
                for entry in entries:
                    json_data.append(entry)
            else:
                for entry in entries:
                    line_count += 1
                    # It is a firewall fix syslogEnabled to false
                    item = entry.get("syslogEnabled")
                    if item:
                        if item.lower() == "false":
                            entry["syslogEnabled"] = False
                        elif item.lower() == "true":
                            entry["syslogEnabled"] = True

                    # Eliminates \n chars from string fields
                    for field in ["srcCidr","destCidr","comment","srcPort","destPort"]:
                        entry[field] = entry[field].replace("\n", "")

                    # force Any to any in protocol fields
                    for field in ["protocol","srcCidr","destCidr","comment","srcPort","destPort"]:
                        entry[field]= entry[field].replace("Any", "any")

                    # validate src and dest ports
                    self.validate_port(entry, "srcPort", line_count)
                    self.validate_port(entry, "destPort", line_count)


                    # For l3fwrules only ensure VLAN Fields are valid
                    if file_type == "l3fwrules" :
                        self.validate_vlan_and_ip(entry, "srcCidr", line_count)
                        self.validate_vlan_and_ip(entry, "destCidr", line_count)
                    else:
                        self.validate_ip_range(entry, "srcCidr", line_count)
                        self.validate_ip_range(entry, "destCidr", line_count)

                    item = entry.get("comment")
                    if item == "Default rule":
                        continue

                    json_data.append(entry)


            Json().writer_full_path(fname_json, json_data)

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
    def fix_bool_to_lower_dict(self, json_data, line):
        for field in json_data.keys():
            data = line[field]
            t = type(data)
            if  t == bool:
                if data is True:
                    line[field]="true"
                else:
                    line[field]="false"
        #return line

    @classmethod
    def fix_bool_to_lower(self, json_data):
        if type(json_data) == list:
            for line in json_data:
                self.fix_bool_to_lower_dict(json_data[0], line)
        else:
            line = json_data
            self.fix_bool_to_lower_dict(json_data, line)

        return json_data

    @classmethod
    def data_to_csv(self, json_data, fname_csv, header=None):
        if type(json_data) == list:
            fieldNames = [k for k in json_data[0].keys()]
        else:
            fieldNames = [k for k in json_data.keys()]

        # Turn boolean field names into strings
        self.fix_bool_to_lower(json_data)

        if header is not None:
            headerOkay=True
            for column in header:
                if column not in fieldNames:
                    headerOkay=False
                    l.logger.error("header column: {} not found".format(column))
                    gv.EOM()
                    gv.fake_assert()
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
            l.logger.error("fname:{}".format(fname_csv))
            l.runlogs_logger.error("fname:{}".format(fname_csv))
            gv.fake_assert()


    @classmethod
    def to_csv(self, fname, header=None, path="data"):
        fname_csv = utils.get_path(fname, path, 'csv')
        obj = Json()
        json_data = obj.reader(fname, path)
        self.data_to_csv(json_data, fname_csv, header)

    @classmethod
    def to_csv_and_validate(self, fname, input_path, output_path):
        fname_json = "{}/{}.json".format(input_path, fname)
        fname_csv = "{}/{}.csv".format(input_path, fname)
        import json as _json
        f = open(fname_json).read()
        json_data = _json.loads(f)
        self.data_to_csv(json_data, fname_csv)

def transform_to_json(fname, absolute_path=None):
    obj=Csv()
    ref = obj.to_json(fname, absolute_path)
    return ref


def transform_to_csv_and_validate(fname, input_path, output_path):
    obj=Csv()
    obj.to_csv_and_validate(fname, input_path, output_path)


def transform_to_csv(fname, header=None, path="data"):
    obj=Csv()
    obj.to_csv(fname, header, path)


if __name__ == '__main__':
    import utils.auto_globals as ag
    ag.folder_time_stamp = '../../data/cli-deploy-s2svpnrules/AutomationTestOrg_DONOTDELETE/2018_03_24_11_59_54/'
    fname = 's2svpnrules_deploy'
    transform_to_csv(fname, header=None, path="ORG")
