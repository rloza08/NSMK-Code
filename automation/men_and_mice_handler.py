#!/usr/bin/env python3
from api.men_and_mice import convert_funnel_patch,  convert_funnel_vlans_add, convert_funnel_vlans_delete
from utils.auto_json import reader, writer
from utils.auto_globals import RUNTIME_DIR

def get_vlans_delete_list(vlans_delete_list):
    convert_funnel_vlans_delete(vlans_delete_list)
    json_funnel_delete_vlans = reader("vlans_delete_list", configDir=RUNTIME_DIR)
    return json_funnel_delete_vlans


if __name__ == '__main__':
    pass
