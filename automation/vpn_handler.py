#!/usr/bin/env python3
import api.vpn as vpn
import utils.auto_json as json
import utils.auto_config as config
import automation.vlan_handler as vlan_handler
import utils.auto_globals as auto_globals

"""
Sets up site to site VPN

First creates all the Vlan Files
(This is done so this module can also be run in
isolation)

Inputs:
	hubnetworks obtained from /config/safeway-config.json
	(specific for that org_name)

		0 = 'N_686798943174004604'
		1 = 'N_686798943174004605'

	lower 
			'10.154.28.0/22'
	upper
			'10.218.28.0/22'

Output:
	call the /api/vpn updated vpn with 
		hubnetworks ['N_686798943174004604', 'N_686798943174004605']	
		subnets: ['10.154.28.0/22', '10.218.28.0/22']

"""


def setupSiteToSiteVpn():
    store_number = auto_globals.store_number
    netid = auto_globals.netid
    config.store_number = store_number

    vlan_handler.createVlanFiles()
    netx = json.reader(config.netx_file)

    # Retrieves hubnetwork for the right org_name
    hubnetworksAllOrgs = config.hubnetworks
    org_name = auto_globals.org_name

    hubnetworks = None
    for item in hubnetworksAllOrgs:
        if item["org_name"] == org_name:
            hubnetworks = item["id"]
            break
    assert (hubnetworks)

    # Generate vpn hubnetworks and vpn-subnets
    defaultroute = config.defaultroute

    upper = "{}/22".format(netx['upper'])
    lower = "{}/22".format(netx['lower'])
    subnets = []
    usevpn = []
    subnets.append(lower)
    usevpn.append(True)  # enable the subnet above
    subnets.append(upper)
    usevpn.append(True)  # enable the subnet above

    # Upload to meraki
    import utils.auto_logger as l
    l.logger.debug("vpn update with hubnetworks: {}".format(hubnetworks))
    l.logger.debug("vpn update with subnets: {}".format(subnets))
    vpn.updatevpnsettings(netid, hubnetworks, defaultroute, subnets, usevpn)
    l.logger.info("vpn updated.") 	

if __name__ == '__main__':
    store_name = "8501"
    org_name = "Ecert_Org2"
    auto_globals.select_org(org_name)
    auto_globals.select_store(store_name)

    setupSiteToSiteVpn()

