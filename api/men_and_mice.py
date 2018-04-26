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
def get_vlan_funnel():
    try:
        cwd = os.getcwd()
        patch = "{}/../config/vlans_funnel.patch.csv".format(cwd)
        src = "{}/../menAndMice/funnel.csv".format(cwd)
        dst = "{}/../config/vlans_funnel.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        shutil.copyfileobj(open(patch, 'rb'), destination)
        destination.close()
        convert_to_json("vlans_funnel", "config",None)
    except:
        l.logger.error("failed")
        assert (0)

if __name__ == '__main__':
    get_vlan_funnel()
