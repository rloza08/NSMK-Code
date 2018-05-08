#!/usr/bin/env python3
"""This module contains the cli interface to the safeway-meraki scripts."""
import os
import fire
import time
import sys
from global_vars import EOM
import global_vars as gv

def lock():
    cnt=0
    while os.path.isfile("CLI_LOCK") is True:
        cnt +=1
        print ("CLI is locked by another process {}", cnt)
        sys.stdout.flush()
        time.sleep(1)
    fp = open("CLI_LOCK", 'w')
    return fp

def unlock(fp):
    fp.close()
    os.unlink("CLI_LOCK")

#used only by the cli
def find_file_pattern(pattern, extension="json"):
    result = []
    cwd = os.getcwd() + "/../../templates"
    files = os.listdir(cwd)
    for file in files:
        pos = file.find(pattern)
        if pos == 0:
            pos = file.find(extension)
            if pos > 0:
                display_name = file.split(".")[0]
                print(display_name)
                result.append(display_name)
    return result


valid_queries = [".", "?", "-h"]

class CLI(object):
    """Class for all the commands , see google fire cli for more information on this."""

    def __init__(self):
        """ Init module only to find out the current directory so we can go down one
            level, execute and then come back to cwd.
        """
        self.cwd = os.getcwd()

    def validate_clone_source(self, clone_source):
        print ("# Valid clone source names  should be in the format 0_Base_Config_vn")
        if str.find(clone_source,"0_Base_Config_v") != 0:
            return False
        return True


    def validate_org_list(self, org_name):
        print ("# List of valid Orgs available #")
        orgs = find_file_pattern("org-")
        if org_name not in orgs:
            if not (org_name in valid_queries):
                print ('"{}" is not a valid org, please select of the orgs from above.'.format(org_name))
            EOM()
            sys.stdout.flush()
            return False
        return True

    def validate_l3fwrules_version(self, version):
        print ("# List of valid l3fwrules available #")
        versions = find_file_pattern("l3fwrules_template")
        if version not in versions:
            if not (version in valid_queries):
                print ('"{}" is not a valid l3fwrules_template, please select one of the valid l3fwrules_template from above.'.format(version))
            EOM()
            sys.stdout.flush()
            return False
        return True

    def validate_s2svpnrules_version(self, version):
        print ("# List of valid s2svpnrules available #")
        versions = find_file_pattern("s2svpnrules_")
        if version not in versions:
            if not (version in valid_queries):
                print ('"{}" is not a valid s2svpnrules, please select one of the valid s2svpnrules from above.'.format(version))
            EOM()
            sys.stdout.flush()
            return False
        return True

    def validate_vlans_add_list(self, vlans_add_list):
        print ("# List of valid vlans-add-lists available")
        vlans_add_lists = find_file_pattern("vlans-add-list-", "csv")
        if vlans_add_list not in vlans_add_lists:
            if not (vlans_add_list in valid_queries):
                print ('"{}" is not a valid vlans-add-list, please select a vlans-add-list from above.'.format(vlans_add_list))
            EOM()
            sys.stdout.flush()
            return False
        return True

    def validate_vlans_delete_list(self, vlans_delete_list):
        print ("# List of valid vlans-delete-lists available")
        vlans_delete_lists = find_file_pattern("vlans-delete-list-", "csv")
        if vlans_delete_list not in vlans_delete_lists:
            if not (vlans_delete_list in valid_queries):
                print ('"{}" is not a valid vlans-delete-list, please select a vlans-delete-list from above.'.format(vlans_delete_list))
            EOM()
            sys.stdout.flush()
            return False
        return True


    def validate_store_list(self, store_list):
        print ("# List of valid Store-lists available")
        store_lists = find_file_pattern("store-list")
        if store_list not in store_lists:
            if not (store_list in valid_queries):
                print ('"{}" is not a valid store-list, please select a valid store-list from above.'.format(store_list))
            EOM()
            sys.stdout.flush()
            return False
        return True


    def set_vlans_add_org(self, org_name):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_org_list(org_name) is False:
            return
        import utils.auto_globals as auto_globals
        print ("\n\n# Selected vlans-add-org #\n{}".format(org_name))
        auto_globals.set_vlans_add_org(org_name)
        EOM()

    def set_vlans_add_store_list(self, store_list):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_store_list(store_list)  is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# Selected vlans-add-store-list #\n{}".format(store_list))
        auto_globals.set_vlans_add_store_list(store_list)
        EOM()

    def set_vlans_add_list(self, vlans_add_list):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_vlans_add_list(vlans_add_list)  is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# Selected vlans-add-list #\n{}".format(vlans_add_list))
        auto_globals.set_vlans_add_list(vlans_add_list)
        EOM()

    def set_vlans_delete_org(self, org_name):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_org_list(org_name) is False:
            return
        import utils.auto_globals as auto_globals
        print ("\n\n# Selected vlans-delete-org #\n{}".format(org_name))
        auto_globals.set_vlans_delete_org(org_name)
        EOM()

    def set_vlans_delete_store_list(self, store_list):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_store_list(store_list)  is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# Selected vlans-delete-store-list #\n{}".format(store_list))
        auto_globals.set_vlans_delete_store_list(store_list)
        EOM()

    def set_vlans_delete_list(self, vlans_delete_list):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_vlans_delete_list(vlans_delete_list)  is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# Selected vlans-delete-list #\n{}".format(vlans_delete_list))
        auto_globals.set_vlans_delete_list(vlans_delete_list)
        EOM()

    def set_networks_org(self, org_name):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_org_list(org_name) is False:
            return
        import utils.auto_globals as auto_globals
        print ("\n\n# Selected networks/sites-org #\n{}".format(org_name))
        auto_globals.set_networks_org(org_name)
        EOM()

    def set_store_lists_org(self, org_name):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_org_list(org_name) is False:
            return
        import utils.auto_globals as auto_globals
        print ("\n\n# Selected store-lists-org #\n{}".format(org_name))
        auto_globals.set_store_lists_org(org_name)
        EOM()

    def set_networks_store_list(self, store_list):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_store_list(store_list)  is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# Selected networks/sites-store-list #\n{}".format(store_list))
        auto_globals.set_networks_store_list(store_list)
        EOM()

    def set_networks_clone_source(self, clone_source):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_clone_source(clone_source)  is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# Selected networks-clone-source #\n{}".format(clone_source))
        auto_globals.set_clone_source(clone_source)
        EOM()

    def set_l3fwrules_org(self, org_name):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_org_list(org_name) is False:
            return
        import utils.auto_globals as auto_globals
        print ("\n\n# selected l3fwrules-org: #\n{}".format(org_name))
        auto_globals.set_l3fwrules_org(org_name)
        EOM()

    def set_l3fwrules_store_list(self, store_list):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_store_list(store_list) is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# selected l3fwrules-store-list: #\n{}".format(store_list))
        auto_globals.set_l3fwrules_store_list(store_list)
        EOM()

    def set_sites_l3fwrules_version(self, version):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_l3fwrules_version(version) is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# selected deploy-l3fwrules-version: #\n{}".format(version))
        auto_globals.set_sites_l3fwrules_version(version)
        EOM()

    def set_l3fwrules_version(self, version):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_l3fwrules_version(version) is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# selected l3fwrules-version: #\n{}".format(version))
        auto_globals.set_l3fwrules_version(version)
        EOM()

    def set_s2svpnrules_org(self, org_name):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_org_list(org_name) is False:
            return
        import utils.auto_globals as auto_globals
        print ("\n\n# selected s2svpnrules-org: #\n{}".format(org_name))
        auto_globals.set_s2svpnrules_org(org_name)
        EOM()

    def set_s2svpnrules_version(self, version):
        os.chdir("{}/automation".format(self.cwd))
        if self.validate_s2svpnrules_version(version) is False:
            return
        import utils.auto_globals as auto_globals
        print("\n\n# selected s2svpnrules-version: #\n{}".format(version))
        auto_globals.set_s2svpnrules_version(version)
        EOM()

    def set_production(self, mode):
        if mode not in [True, False, "true", "false", "True", "False", "on", "off"]:
            print("Invalid  production flag (True or False")
            return
        if mode in [True, "true", "True", "on"]:
            real_mode = True
        elif mode in [False, "false", "False","off"]:
            real_mode = False

        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        print("\n\n# selected production:  {}#".format(real_mode))
        auto_globals.set_production(real_mode)
        EOM()

    def set_run_dry(self):
        """This is the default and selects dry-run mode which bypaasses meraki api calls ,
        It is useful to verify valid org name, store id and that the scripts are running
        okay. This will generate all the logs also on ./data/<fname>.log"""
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        auto_globals.set_run_dry(True)
        print ("\n\n# selected run-dry #")
        os.chdir("{}".format(self.cwd))
        EOM()

    def set_run_normal(self):
        """Selects normal run mode which makes meraki api calls"""
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        auto_globals.set_run_dry(False)
        print ("\n\n# selected run-normal #")
        os.chdir("{}".format(self.cwd))
        EOM()

    def select(self, module, param):
        """
            Modulesdepl
                networks-org
                networks-store-list
                networks-clone-source
                sites-org
                sites-store-list
                sites-l3fwrules-version
                store-lists-org
                vlans-add-org
                vlans-add-store-list
                vlans-add-list
                vlans-delete-org
                vlans-delete-store-list
                vlans-delete-list
                l3fwrules-org
                l3fwrules-store-list
                l3fwrules-version
                s2svpnrules-org
                s2svpnrules-version
        """

        if module.find("networks-org") == 0:
            self.set_networks_org(org_name=param)
        elif module.find("sites-org") == 0:
            self.set_networks_org(org_name=param)
        elif module.find("networks-store-list") == 0:
            self.set_networks_store_list(store_list=param)
        elif module.find("networks-clone-source") == 0:
            self.set_networks_clone_source(clone_source=param)
        elif module.find("sites-store-list") == 0:
            self.set_networks_store_list(store_list=param)
        elif module.find("sites-l3fwrules-version") == 0:
            self.set_sites_l3fwrules_version(version=param)
        elif module.find("store-lists-org") == 0:
            self.set_store_lists_org(org_name=param)
        elif module.find("vlans-add-org") == 0:
            self.set_vlans_add_org(org_name=param)
        elif module.find("vlans-add-store-list") == 0:
            self.set_vlans_add_store_list(store_list=param)
        elif module.find("vlans-add-list") == 0:
            self.set_vlans_add_list(vlans_add_list=param)
        elif module.find("vlans-delete-org") == 0:
            self.set_vlans_delete_org(org_name=param)
        elif module.find("vlans-delete-store-list") == 0:
            self.set_vlans_delete_store_list(store_list=param)
        elif module.find("vlans-delete-list") == 0:
            self.set_vlans_delete_list(vlans_delete_list=param)
        elif module.find("l3fwrules-org") == 0:
            self.set_l3fwrules_org(org_name=param)
        elif module.find("l3fwrules-store-list") == 0:
            self.set_l3fwrules_store_list(store_list=param)
        elif module.find("l3fwrules-version") == 0:
            self.set_l3fwrules_version(version=param)
        elif module.find("s2svpnrules-org") == 0:
            self.set_s2svpnrules_org(org_name=param)
        elif module.find("s2svpnrules-version") == 0:
            self.set_s2svpnrules_version(version=param)
        elif module.find("production") == 0:
            self.set_production(mode=param)
        elif module.find("run") == 0:
            if param == "dry":
                self.set_run_dry()
            else:
                self.set_run_normal()
        else:
            print ("Invalid command {}". format(module))

    # def get_status(self):
    #     """Shows the status : Org Name, Org Id, Store Name, Store Id and netid for the store"""
    #     os.chdir("{}/automation".format(self.cwd))
    #     import utils.auto_doc as auto_doc
    #     auto_doc.show_status()
    #     os.chdir("{}".format(self.cwd))

    def	get_l3fwrules(self):
        """Runs the store orchestration"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.firewall_handler import bulk_get
        agent = "cli-get-l3fwrules"
        bulk_get(agent=agent)
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def	get_s2svpnrules(self):
        """Runs the store orchestration"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.vpn_firewall_handler import bulk_get
        agent = "cli-get-s2svpnrules"
        bulk_get(agent=agent)
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def get_settings_all(self):
        """Selects normal run mode which makes meraki api calls"""
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()

        EOM()
        print ("# Valid Orgs available #")
        find_file_pattern("org-")
        EOM()
        print ("# Valid Store Lists available #")
        find_file_pattern("store-list")

        EOM()
        print ("# Valid Vlans Add Lists available #")
        find_file_pattern("vlans-add-list")

        EOM()
        print ("# Valid Vlans Delete Lists available #")
        find_file_pattern("vlans-delete-list")

        EOM()
        print ("# deploy vlans-add settings #")
        for key in settings:
            if key.find("vlans-add")==0:
                print ("{}:  {}".format(key, settings[key]))

        EOM()
        print ("# deploy vlans-delete settings #")
        for key in settings:
            if key.find("vlans-add")==0:
                print ("{}:  {}".format(key, settings[key]))

        EOM()
        print ("# Valid l3fwrules available #")
        find_file_pattern("l3fwrules_template")

        EOM()
        print ("# Valid s2svpnrules available #")
        find_file_pattern("s2svpnrules_")

        EOM()
        print ("# deploy networks/stores settings #")
        for key in settings:
            if key.find("deploy")==0:
                print ("{}:  {}".format(key, settings[key]))

        EOM()
        print ("# l3fwrules settings #")
        for key in settings:
            if key.find("l3fwrules")==0:
                print ("{}:  {}".format(key, settings[key]))

        EOM()
        print ("# s2svpnrules settings #")
        for key in settings:
            if key.find("s2svpnrules")==0:
                print ("{}:  {}".format(key, settings[key]))

        EOM()
        print ("# Available commands #")
        print ("   select <parameter> <value> ")
        print ("   get settings  all")
        print ("   get settings  networks")
        print ("   get settings  sites")
        print ("   get settings  store-lists")
        print ("   get settings  vlans-add")
        print ("   get settings  vlans-delete")
        print ("   get settings  l3fwrules")
        print ("   get settings  s2svpnrules")
        print ("   deploy networks ")
        print ("   deploy sites")
        print ("   deploy l3fwrules")
        print ("   deploy s2svpnrules")
        print ("   get store-lists")
        print ("   get l3fwrules")
        print ("   get s2svpnrules")
        print ("   convert csv-to-json <filename in /appl/nms/xfer")
        print ("   convert json-to-csv <filename in /appl/nms/xfer")
        EOM()
        print ("")
        os.chdir("{}".format(self.cwd))

    def get_settings_sites(self):
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()
        EOM()
        print ("# sites settings #")
        for key in settings:
            if key.find("sites")==0:
                print ("{}:  {}".format(key, settings[key]))

        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")

    def get_settings_networks(self):
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()
        EOM()
        print ("# networks settings #")
        for key in settings:
            if key.find("networks")==0:
                print ("{}:  {}".format(key, settings[key]))

        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")

    def get_settings_vlans_add(self):
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()
        EOM()
        print ("# deploy vlans-add settings #")
        for key in settings:
            if key.find("vlans-add")==0:
                print ("{}:  {}".format(key, settings[key]))

        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")

    def get_settings_vlans_delete(self):
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()
        EOM()
        print ("# deploy vlans-delete settings #")
        for key in settings:
            if key.find("vlans-delete")==0:
                print ("{}:  {}".format(key, settings[key]))

        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")


    def get_settings_l3fwrules(self):
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()
        EOM()
        print ("# l3fwrules settings #")
        for key in settings:
            if key.find("l3fwrules")==0:
                print ("{}:  {}".format(key, settings[key]))

        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")

    def get_store_lists(self):
        """Runs the store list"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.network_handler import get_store_lists
        agent = "cli-get-store_list"
        get_store_lists(agent=agent)
        sys.stdout.flush()
        time.sleep(1)
        EOM()
        print ("# store lists have been created #")
        return True

    def get_settings_s2svpnrules(self):
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()
        EOM()
        print ("# s2svpnrules settings #")
        for key in settings:
            if key.find("s2svpnrules")==0:
                print ("{}:  {}".format(key, settings[key]))

        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")

    def get_settings_store_lists(self):
        os.chdir("{}/automation".format(self.cwd))
        import utils.auto_globals as auto_globals
        settings = auto_globals.get_cli_settings()
        EOM()
        print ("# store-lists settings #")
        for key in settings:
            if key.find("store-lists")==0:
                print ("{}:  {}".format(key, settings[key]))

        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")


    def update_vlan_template(self):
        os.chdir("{}/automation".format(self.cwd))
        from automation.vlan_handler import update_vlan_template
        update_vlan_template()
        EOM()
        print ("# vlan template has been updated #")
        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")

    def update_funnel(self):
        os.chdir("{}/automation".format(self.cwd))
        from automation.men_and_mice_handler import update_funnel
        update_funnel()
        EOM()
        print ("# funnel file has been updated #")
        os.chdir("{}".format(self.cwd))
        EOM()
        print ("")


    def update(self, module):
        """
            Modules

                funnel
                vlan-settings
        """
        if module.find("vlan-template") >= 0:
                self.update_vlan_template()
                return

        if module.find("funnel") >= 0:
                self.update_funnel()
                return


    def get(self, module, param=None):
        """
            Modules

                settings
        """
        if module.find("l3fwrules") >= 0:
                self.get_l3fwrules()
                return
        if module.find("store-lists") >= 0:
                success = self.get_store_lists()
                return
        if module.find("s2svpnrules") >= 0:
                self.get_s2svpnrules()
                return
        if module.find("settings") >= 0:
            if param == "all":
                self.get_settings_all()
            elif param == "l3fwrules":
                self.get_settings_l3fwrules()
            elif param == "store-lists":
                self.get_settings_store_lists()
            elif param == "s2svpnrules":
                self.get_settings_s2svpnrules()
            elif param == "sites":
                self.get_settings_sites()
            elif param == "networks":
                self.get_settings_networks()
            elif param == "vlans-add":
                self.get_settings_vlans_add()
            elif param == "vlans-delete":
                self.get_settings_vlans_delete()
            else:
                print("Invalid option.")
        else:
            print ("Invalid option.")

    def convert_csv_to_json(self, fname):
        _fname = fname.split(".")
        fname = _fname[0]
        if len(_fname)>1:
            if (_fname[1] != "csv"):
                print("Invalid file name, must end with csv and be in home directory.")
                gv.fake_assert()
        os.chdir("{}/automation".format(self.cwd))
        from utils.auto_csv import convert_to_json_and_validate
        if os.name == 'nt':
            input_path = output_path = "c:\\nms\\xfer"
        else:
            input_path = "/appl/nms/xfer/"
            output_path = input_path
        convert_to_json_and_validate(fname, input_path,output_path)
        os.chdir("{}".format(self.cwd))
        print("{}.json has been created in {} \n".format(fname, output_path))
        EOM()

    def convert_json_to_csv(self, fname):
        _fname = fname.split(".")
        fname = _fname[0]
        if len(_fname)>1:
            if (_fname[1] != "json"):
                print("Invalid file name, must end with json and be in home directory.")
                gv.fake_assert()
        os.chdir("{}/automation".format(self.cwd))
        from utils.auto_csv import convert_to_csv_and_validate
        if os.name == 'nt':
            input_path = output_path = "c:\\nms\\xfer"
        else:
            input_path = "/appl/nms/xfer/"
            output_path = input_path
        convert_to_csv_and_validate(fname, input_path,output_path)
        os.chdir("{}".format(self.cwd))
        print("{}.csv has been created in {}\n".format(fname, output_path))
        EOM()

    def convert(self, module, fname):
        """
            Modules

                csv-to-json
                json-to-csv
        """
        if module.find("csv-to-json") >= 0:
            self.convert_csv_to_json(fname)
        elif module.find("json-to-csv") >= 0:
            self.convert_json_to_csv(fname)
        else:
            print ("Invalid option.")

    def	deploy(self, module):
        """
            Modules
                    networks
                    sites
                    l3fwrules
                    s2svpnrules
                    vlans-add
                    vlans-delete
        """
        if module.find("sites")>=0:
            self.deploy_sites()
        elif module.find("vlans-add") >= 0:
                self.deploy_vlans_add()
        elif module.find("vlans-delete") >= 0:
                self.deploy_vlans_delete()
        elif module.find("networks")>=0:
            self.deploy_networks()
        elif module.find("l3fwrules")>=0:
            self.deploy_l3fwrules()
        elif module.find("s2svpnrules")>=0:
            self.deploy_s2svpnrules()
        else:
            print ("Invalid option.")


    # Should get config (shows all the gets)
    def	deploy_sites(self):
        """Runs the store orchestration"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.sites_handler import bulk_update
        agent = "cli-deploy-sites"

        #text = raw_input("deploy stores (y/N)")
        bulk_update(agent)
        os.chdir("{}".format(self.cwd))
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def	deploy_vlans_add(self):
        """Runs the store orchestration"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.sites_handler import bulk_update
        agent = "cli-deploy-vlans-add"
        bulk_update(agent, vlans_only=True)
        os.chdir("{}".format(self.cwd))
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def deploy_vlans_delete(self):
        """Runs the store orchestration"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.sites_handler import bulk_update
        agent = "cli-deploy-vlans-delete"
        bulk_update(agent, vlans_only=True)
        os.chdir("{}".format(self.cwd))
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def	deploy_networks(self):
        """Runs the store orchestration"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.network_handler import bulk_deploy_networks_for_all_orgs
        bulk_deploy_networks_for_all_orgs(agent="cli-deploy-networks")
        os.chdir("{}".format(self.cwd))
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def	deploy_l3fwrules(self):
        """Runs the store orchestration"""
        os.chdir("{}/automation".format(self.cwd))
        from automation.firewall_handler import bulk_update
        agent = "cli-deploy-l3fwrules"
        bulk_update(agent=agent)
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def	deploy_s2svpnrules(self):
        """Runs vpn firewall bulk update"""
        os.chdir("{}/automation".format(self.cwd))
        import automation.vpn_firewall_handler as vpn_firewall_handler
        agent = "cli-deploy-s2svpnrules"
        vpn_firewall_handler.bulk_update(agent)
        os.chdir("{}".format(self.cwd))
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def how_to(self, config=None, templates=None, commands=None):
        """Shows all the possible how tos for these automation scripts"""
        os.chdir("{}/automation".format(self.cwd))
        from utils.auto_doc import howto
        howto(config, templates, commands)
        os.chdir("{}".format(self.cwd))
        sys.stdout.flush()
        time.sleep(1)
        EOM()

    def doc(self, design=None, automation=None, automation_vlan=None,
            automation_firewall=None, automation_vpn_handler=None,
            api=None, api_vlans=None, api_meraki=None, api_netx=None,
            config=None, utils=None, men_and_mice=None, data=None):
        """Provides internal documentation on the safeway-meraki scripts"""

        os.chdir("{}/automation".format(self.cwd))
        from utils.auto_doc import doc
        doc(design, automation, automation_vlan,
            automation_firewall, automation_vpn_handler,
            api, api_vlans, api_meraki, api_netx,
            config, utils, men_and_mice, data)
        os.chdir("{}".format(self.cwd))
        sys.stdout.flush()
        time.sleep(1)
        EOM()

if __name__ == '__main__':
    #fp = lock()
    fire.Fire(CLI)
    #unlock(fp)
