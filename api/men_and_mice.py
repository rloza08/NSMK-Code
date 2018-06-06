#!/usr/bin/env python3
import os
import shutil
import sys
from utils.auto_csv import convert_to_json
import utils.auto_logger as l
from utils.auto_globals import CONFIG_DIR, RUNTIME_DIR
from utils.auto_json import writer

cwd = os.getcwd()
path = "{}/..".format(cwd)
sys.path.insert(0, path)


"""
Calls the men and mice get funnel process, which 
is python 2.7 code, based inside this project
(menAndMice)

The getFunnel.py queries men and mice and creates
a file in its directory

this function will then copy this into the data directory
where the it will be picked up by the vlan_handler module.

"""
from subprocess import Popen, PIPE
import csv
from utils.auto_json import make_pretty
from utils.low_csv import Csv

def transform_funnel_NETX_to_10_x():
    src = "../menAndMice/funnel.csv".format(cwd)
    dst = "{}/vlans-funnel-NETX.csv".format(RUNTIME_DIR)
    destination = open(dst, 'wb')
    shutil.copyfileobj(open(src, 'rb'), destination)
    destination.close()

    src = "{}/vlans-funnel-NETX.csv".format(RUNTIME_DIR)
    entries = []
    with open(src, encoding="windows-1251", newline='') as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True, fieldnames=["Vlan", "Subnet", "Description"])
        header = True
        for entry in reader:
            if header:
                header = False
                continue
            subnet = entry["Subnet"].lower()
            subnet = subnet.replace("net", "10.x.")
            entry["Subnet"] = subnet
            entries.append(entry)
    writer("vlans-funnel-base", entries, RUNTIME_DIR)


def get_and_convert_funnel():
    try:
        cwd = os.getcwd()
        # Our base dir is ./automation
        os.chdir("{}/../menAndMice".format(cwd))
        p = Popen("{}/../menAndMice/getFunnel.py".format(cwd), shell=True, stdout=PIPE)
        resp = p.communicate()[0].decode("utf-8")
        print (resp)
        os.chdir(cwd)
        transform_funnel_NETX_to_10_x()

    except:
        l.logger.error("failed")
        assert(0)

def convert_funnel_patch(use_vlans_add=False, use_vlans_delete=False):
    try:
        cwd = os.getcwd()
        src = "{}/vlans_funnel_patch.csv".format(CONFIG_DIR)
        dst = "{}/vlans_funnel_patch.csv".format(RUNTIME_DIR)
        source = open(src, 'rb')
        destination = open(dst, 'wb')
        shutil.copyfileobj(source, destination)
        convert_to_json("vlans_funnel_patch", "runtime",None)
    except:
        l.logger.error("failed")
        assert (0)

def convert_funnel_vlans_add(vlans_add_list):
    try:
        cwd = os.getcwd()
        source = "{}/../../templates/{}.csv".format(cwd, vlans_add_list)
        destination = "{}/vlans_add_list.csv".format(RUNTIME_DIR)
        shutil.copyfileobj(open(source, 'rb'), open(destination, 'wb'))
        convert_to_json("vlans_add_list", "runtime", None)

    except:
        l.logger.error("convert_funnel_vlans_add failed")
        assert (0)

def convert_funnel_vlans_delete(vlans_delete_list):
    try:
        cwd = os.getcwd()
        source = "{}/../../templates/{}.csv".format(cwd, vlans_delete_list)
        destination = "{}/vlans_delete_list.csv".format(RUNTIME_DIR)
        shutil.copyfileobj(open(source, 'rb'), open(destination, 'wb'))
        convert_to_json("vlans_delete_list", "runtime", None)

    except:
        l.logger.error("failed")
        assert (0)


if __name__ == '__main__':
    cwd = os.getcwd()
    os.chdir("{}/automation".format(cwd))
    transform_funnel_NETX_to_10_x()

