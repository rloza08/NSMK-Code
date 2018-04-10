from subprocess import Popen
import subprocess as p
import os

def call_automation(func, no_wait=False):
    cwd = os.getcwd()
    print (cwd)
    result=None
    cmd = "python3 cli.py {}".format(func)
    print (cmd)
    proc = Popen(cmd.split(), stdout=p.PIPE, cwd="{}/..".format(cwd), stderr=p.PIPE)
    if no_wait is False:
        stdout, stderr = proc.communicate()
        str = stdout.decode("ascii")
        result = str.splitlines()
    return result

def get_firewall_l3_versions():
    fwlist = call_automation("list-l3-versions")
    print (fwlist)
    return fwlist

def get_store_groups():
    store_list = call_automation("get-store-list")
    return store_list

def get_firewall_s2s_versions():
    fwlist = call_automation("list-vpn-versions")
    return fwlist

def get_org_groups():
    org_list = call_automation("get-org-list")
    return org_list

def bulk_deploy_l3(org_group, fw_l3_version, store_group):
    cmd = "firewall-update-bulk  {} {} {}".format(org_group, fw_l3_version, store_group)
    print ("deploying to org-group: {} fw_l3 version : {} to group : {}".format(org_group, fw_l3_version, store_group))
    result = call_automation(cmd, no_wait=False)

def bulk_deploy_s2s(org_group, fw_s2s_version):
    cmd = "vpn-firewall-update-bulk  {} {}".format(org_group, fw_s2s_version)
    print ("deploying fw_l2 version : {} to org : {}".format(fw_s2s_version, org_group))
    result = call_automation(cmd, no_wait=False)

if __name__ == '__main__':
    get_firewall_l3_versions()