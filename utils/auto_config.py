#!/usr/bin/env python3
import os
import json
import utils.auto_logger as l
import global_vars as gv

global clone_id
clone_id = None

def make_pretty(my_json):
    return (json.dumps(my_json, indent=4, sort_keys=False))

def json_reader(fpath):
    data = None
    try:
        json_data = open(fpath).read()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
        str = make_pretty(data)
    except Exception as err:
        # l.logger.error("exception failure fpath:{} {}".format(fpath))
        # l.runlogs_logger.error("exception failure fpath:{} {}".format(fpath))
        gv.fake_assert()
    return data

def json_writer(fpath):
    data = None
    try:
        json_data = open(fpath).write()
        # json_data = json_data.replace("\n","")
        data = json.loads(json_data)
        str = make_pretty(data)
        l.logger.debug("auto_utils.json_reader:\n{}".format(str))
    except Exception as err:
        l.logger.error("fpath:{} {}".format(fpath))
        l.runlogs_logger.error("fpath:{} {}".format(fpath))
        gv.fake_assert()
    return data

def setup_proxy():
    user = os.environ.get("PROXY_USER", None)
    password = os.environ.get("PROXY_PWD", None)
    if not user and not password:
        return
    if user and password:
        url = "http://{}:{}@phxproxyvip.safeway.com:8080".format(user, password)
    else:
        url = "http://culproxyvip.safeway.com:8080"
    os.environ['HTTPS_PROXY'] = url

def set_clone_id(id):
    global clone_id
    clone_id = id

def get_clone_id():
    global clone_id
    return clone_id

def init_config():
    global api_key
    api_key = os.environ.get("API_KEY", None)
    assert(api_key)
    setup_proxy()

init_config()