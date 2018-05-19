#!/usr/bin/env python3
import json
# from utils.auto_logger import logger, runlogs_logger
import global_vars as gv
import os

settings = {}

def json_reader(fpath):
    data = None
    cwd = os.getcwd()
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
    except Exception as err:
        # logger.error("cwd {} fpath {}".format(cwd, fpath))
        # runlogs_logger.error("cwd {} fpath {}".format(cwd, fpath))
        gv.fake_assert()

    return data


def load_settings():
    global settings
    settings["CLI"] = json_reader("../runtime/cli-selections.json")

def pmdb_init():
    global settings
    load_settings()
    settings["org-name"] = None
    settings["store-name"]= None
    settings["agent"] = None
    settings["org-id"] = None
    settings["folder-time-stamp"] = None
    settings["store-name"] = None
    settings["store-number"] = None
    settings["time-stamp"] = None
    settings["netid"] = None
    settings["device-name"] = None
    settings["serial"] = None
