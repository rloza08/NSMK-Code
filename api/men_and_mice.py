#!/usr/bin/env python3
import os
import shutil
import sys
from utils.auto_csv import convert_to_json
import utils.auto_logger as l

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

def convert_funnel():
    try:
        cwd = os.getcwd()
        src = "{}/../menAndMice/funnel.csv".format(cwd)
        dst = "{}/../runtime/vlans_funnel_base.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        destination.close()
        convert_to_json("vlans_funnel_base", "runtime",None)

    except:
        l.logger.error("failed")
        assert (0)

def convert_funnel_patch(use_vlans_add=False, use_vlans_delete=False):
    try:
        cwd = os.getcwd()
        src = "{}/../../config/vlans_funnel_patch.csv".format(cwd)
        dst = "{}/../runtime/vlans_funnel_patch.csv".format(cwd)
        source = open(src, 'rb')
        destination = open(dst, 'wb')
        shutil.copyfileobj(source , destination)
        convert_to_json("vlans_funnel_patch", "runtime",None)
    except:
        l.logger.error("failed")
        assert (0)

def convert_funnel_vlans_add(vlans_add_list):
    try:
        cwd = os.getcwd()
        source = "{}/../../templates/{}.csv".format(cwd, vlans_add_list)
        destination = "{}/../runtime/vlans_add_list.csv".format(cwd)
        shutil.copyfileobj(open(source, 'rb'), open(destination, 'wb'))
        convert_to_json("vlans_add_list", "runtime", None)

    except:
        l.logger.error("convert_funnel_vlans_add failed")
        assert (0)

def convert_funnel_vlans_delete(vlans_delete_list):
    try:
        cwd = os.getcwd()
        source = "{}/../../templates/{}.csv".format(cwd, vlans_delete_list)
        destination = "{}/../runtime/vlans_delete_list.csv".format(cwd)
        shutil.copyfileobj(open(source, 'rb'), open(destination, 'wb'))
        convert_to_json("vlans_delete_list", "runtime", None)

    except:
        l.logger.error("failed")
        assert (0)


if __name__ == '__main__':
    pass

