#!/usr/bin/env python3
from api.men_and_mice import convert_funnel_patch,  convert_funnel_vlans_add, convert_funnel_vlans_delete
from utils.auto_json import reader, writer
from utils.auto_globals import RUNTIME_DIR

def get_vlans_delete_list(vlans_delete_list):
    convert_funnel_vlans_delete(vlans_delete_list)
    json_funnel_delete_vlans = reader("vlans_delete_list", configDir=RUNTIME_DIR)
    return json_funnel_delete_vlans

# def create_funnel_vlans(add_vlans_list=None):
#     # Base funnel and 995 patch is always used
#     convert_funnel_patch()
#     json_funnel_base = reader("vlans_funnel_base", configDir="config")
#     json_funnel_patch = reader("vlans_funnel_patch", configDir="config")
#     json_funnel = json_funnel_base + json_funnel_patch
#     if add_vlans_list:
#         convert_funnel_vlans_add(add_vlans_list)
#         json_funnel_add_vlans = reader("vlans_add_list", configDir="runtime")
#         json_funnel += json_funnel_add_vlans
#
#     writer("vlans_funnel", json_funnel, "config")
#     return json_funnel

if __name__ == '__main__':
    pass
