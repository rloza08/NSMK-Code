

howto = \
"""
    config            : for help on how to configure handlers (vlan, firewall and vpn)
    templates         : for help on firewall and vlan templates
    commands          : for help on available commands
    s2s-vpn-rules     : for help on s2s-vpn-rules
    l3-firewall       : for help on l3-firewall
"""

howto_config = \
    """
            Configuration is done on four(4) locations:
    
            (I) ./templates directory
                 This is where all the templates for file generation are located.
        
                 vlan_set_template.json
                  - Contains the template for the jinja based vlan_generated_xxx.json files
                    which are used to create individual calls by making the proper meraki api calls.
                  - This file is based on a Meraki VLAN template and it follows the same pattern
                    (hence for more information see the meraki documentation)
                 firewall_template.json
                  - Contains the template for the generation of firewalls for each store/network.
                    This is essentially a tamplate VLAN based firewall used by meraki.
                    For more information see the respective meraki documentation.
    
            (II) ./config/safeway-utils.json
                 This is where orchestration handler configuration goes.
                 - The main sections are:
                   - vlan
                   - firewall
                   - vpn
    
            (III) ./config/safeway-orgs.json
                This file contains the list of supported orgs currently support.
                New orgs should have their names and ids added here.
                Orgs are in the format :
                  {
                    "id": 686798943174000753,
                    "name": "Ecert_Org"
                    },
                (hints: 
                    use the Pycharm editor, which will validate the json file.
                    no red marked item should exist)
                    don't forget to add the comma (,) after the entry, unless this
                    is the last try on the json list.
                    
    
                To see all included orgs please run: ./cli show-status 
    
            (IV) ../safeway-personal.json
                This is where the personal information is located.
                It is one level up from the repository as it should not be
                saved into github.
                
                It contains proxy user id and passwords. (to be hashed in the future)
                It will also contain men and mice user and password (to be hashed in the future)
"""

howto_template = \
"""
        Template configuration is located in the
        /templates directory

         vlan_set_template.json
          - Contains the template for the jinja based vlan_generated_<netid>.json files
            which are used to create individual calls by making the proper meraki api calls.
          - This file is based on a Meraki VLAN template and it follows the same pattern
            (hence for more information see the meraki documentation)
            
         firewall_template.json
          - Contains the template for the generation of firewalls for each store/network.
            This is essentially a tamplate VLAN based firewall used by meraki.
            For more information see the respective meraki documentation.

"""

howto_commands = \
"""
    The available commands are:
    
    (1) store-orchestration:
        Runs the full store scripts (vlan-handlers, static-route, firewall, vpnsetup)
        for a given Store (store name) and organization (org name)
    
    (2) show-status
        Shows: 
            - org in use (org name and org id provided)
            - store in use
            - netid for the store
            
        Lists all the orgs that are currently available for this script.
        New orgs need to have their org name and org id added to 
        the ./config/config-orgs.json file
        
    (3) select-store 
        Points to the store name to be used.
        
    (4) select-org 
        Points to the org name to be used.
        

    (4) how-to
        Provides a list of howto's regarding this script
    
    (5) doc
        Provides documentation regarding the structure
        and each individual modules.
        Helpful for debugging and support.
        
    (6) dry-run
        dryrun - selects dryrun mode where no meraki api calls are made, only a
        call to the networlist is done in order to establish the netid
        
    (7) get-store-netid
        Makes a network list query and retrieves the proper netid for that store
        (requires that org-name and store-name have been set previously)
            
"""

howto_l3_firewall = \
    """
        Environment setup:
    
        (1) Add to your API_KEY
            in case you haven't already done so.
            > echo export API_KEY=xxxxxxxxxxxxx >> ~/.bashrc
            > echo export http_proxy=http://culproxyvip.safeway.com:8080  >> ~/.bashrc
            > echo export https_proxy=https://culproxyvip.safeway.com:8080  >> ~/.bashrc
            > echo export cd /appl/nsmk/nsmk-server  >> ~/.bashrc
    
        (2) Show all available org groups:
            > ./cli.py  get-org-list
                org-Store_QA_Org
                org-New_Production_MX_Org
                org-AutomationTestOrg_DONOTDELETE       

        (3) Show all available store groups:
            > ./cli.py get-store-list
                -INT
                -SHA
                store-list-JEW
                store-list-SWY              
            
        (4) Show l3 firewall templates:
            > ./cli.py show-l3-firewall-versions
                firewall_rules_template_003
                firewall_rules_template_004
                firewall_rules_template_005
        
        (5) Deploy L3 Firewalls:
            e.g.
            >./cli.py deploy-l3-firewall  org-AutomationTestOrg_DONOTDELETE firewall_rules_template_004 store-list-SHA
                        
    """
howto_s2s_vpn_rules = \
    """
        Environment setup:

        (1) Add to your API_KEY
            in case you haven't already done so.
            > echo export API_KEY=xxxxxxxxxxxxx >> ~/.bashrc
            > echo export http_proxy=http://culproxyvip.safeway.com:8080  >> ~/.bashrc
            > echo export https_proxy=https://culproxyvip.safeway.com:8080  >> ~/.bashrc
            > echo export cd /appl/nsmk/nsmk-server  >> ~/.bashrc
            
        (2) Show all available org groups:
            > ./cli.py  get-org-list
                org-Store_QA_Org
                org-New_Production_MX_Org
                org-AutomationTestOrg_DONOTDELETE       

        (3) Show all s2s-vpn firewall templates:
            > ./cli.py show-vpn-versions
                S2S_VPN_Rules_001
                S2S_VPN_Rules_001c
                S2S_VPN_Rules_001a
                S2S_VPN_Rules_001b

        (4) Deploy S2S-VPN Rules:
            >./cli.py deploy-s2s-vpn-rules org-AutomationTestOrg_DONOTDELETE S2S_VPN_Rules_001

    """

doc=\
"""
        Documentation is available for the following topics
        
    --design                : overview on the structure and design
    --automation            : automation module doc
    --automation_vlan       : vlan automation handler doc
    --automation_firewall   : firewall automatioon handler
    --automation_vpn_handler: vpn automation handler doc
    --api                   : low level api doc
    --api-vlans             : detailed vlans api doc
    --api-meraki            : meraki api doc 
    --api-item              : meraki api doc 
    --config                : config module doc
    --utils                 : utils module doc
    --men-and-mice: men and mice doc
    --data                  : data directory contents
"""

doc_design=\
"""
The scripts are divided in the following modules:
    - api : Contains scripts that interact external depencies via APIs.
            They are :
                meraki-api used to access meraki
                men-and-mice in order to access men and mice and
                    retrieve the funnel csv file
                netx - used to discover the upper and lower subnets for the store.
                
    - automation :
            Contains handlers that perform some logic and eventually access
            one or more api modules
            The handlers used are: vlan, firewall, static route and vpn.
    - config :
            auto_utils.py - loads configuration from:
                - ./config/safeway-utils.json (has configuration info for handlers)
                - ../../safeway-personal.json (has user personal info, eg. proxy uid and pwd)
                - ./config/safeway-orgs.json   (contains the list of supported orgs by
                this script)
                
            auto-globals.py

    - data :
            All interim data is stored here.        
            A time-stamp directory is created for every org, store and run in
            the format : /data/<org_name>/<store_name>/<time_stamp>/< actual files>
            
            
            By default the logger will place it is log files in the base /data directory
            (It is possible to redirect log messages to another directory, see doc_utils 
            info on the logger for more on this.
            
            A copy of the latest vlans_funnell.csv obtained from men and mice.
                        
"""
doc_automation=\
"""
            The /automation directory contains handlers used by 
            the store_orchestration:
               vlan, firewall, static route and vpn.
               
            No direct api calls are made directly from this module.
            
"""

doc_automation_vlan=\
"""
            The /automation/vlan_handler is reponsible for creating/updating
            the /data/<org_name>/<store_name>/<timestamp>/vlans_generated_<netid>.json
            
            This file is used by /api/vlan driver that calls the meraki api.
            
            The overall flow of vlan creation/updates is as follows:
            
            - /data/<org_name>/<store_name>/<timestamp>/vlans_funnel.csv
            (obtained from /api/men_and_mice)
            and 
              /data/<org_name>/<store_name>/<timestamp>/vlans_netx.json
            (obtained from /api/item)
            
            are used to create a vlan table
              /data/<org_name>/<store_name>/<timestamp>/vlans_funnel_table.json
            
            {
                "1": "10.218.28.16/27",
                "14": "10.218.28.248/29",
                "16": "10.218.29.0/24",
            ...
            
            The final step is to generate the 
              /data/<org_name>/<store_name>/<timestamp>/vlans_generated_<netid>.json
              
            This is done using jinja2 (the context comes the vlans Table (above)
            and the jinja template used is
            ./templates/vlans_set_templates.json
            
            For more detailed information please look into the actual
            ./automation/vlan_handler.py and 
            ./api/vlan.py
                                 
"""
doc_automation_firewall=\
"""
            The firewall updates are handled by the
            /automation/firewall_handler
            
            This is not a jinja2 template but still uses :
            - a template file /templates/firewall_template.json
            This template is essentially a meraki VLAN template.
            
            - The actual octects are adjusted by the handler using item and vlan table
            
"""

doc_automation_vpn_handler = \
"""
doc_automation_vpn_handler
"""

doc_api=\
"""
doc_api
"""

doc_api_vlans=\
"""
doc_api_vlans
"""

doc_api_meraki=\
"""
doc_api_meraki
"""

doc_api_netx=\
"""
doc_api_netx
"""

doc_config=\
"""
doc_api_config
"""

doc_utils=\
"""
doc_utils
"""

doc_men_and_mice=\
"""
doc_men_and_mice
"""

doc_data=\
"""
doc_data
"""

