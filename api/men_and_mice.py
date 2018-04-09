#!/usr/bin/env python3
import os
from subprocess import Popen, PIPE
import shutil
import sys

cwd = os.getcwd()
path = "{}/..".format(cwd)
sys.path.insert(0, path)

import utils.auto_logger as l

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
        dst = "{}/../data/vlans_funnel.csv".format(cwd)
        destination = open(dst, 'wb')
        shutil.copyfileobj(open(src, 'rb'), destination)
        shutil.copyfileobj(open(patch, 'rb'), destination)
        destination.close()

    except:
        l.logger.error("failed")
        assert (0)

if __name__ == '__main__':
    get_vlan_funnel()
