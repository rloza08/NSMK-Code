#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_json as json
from utils.auto_logger import runlogs_logger, logger
from api.meraki_patch import meraki
import global_vars as gv


class Vlans(object):

    """
    Creates and updates VLAN.
    Creates if it does not exist or updates if it is an existing one.

    """

    @classmethod
    def create_update_vlans_list(self, netid, update_flag=True):
        fname = "vlans_generated_{}".format(netid)
        vlans_to_deploy = json.reader(fname)
        self.get_vlans(netid)
        vlans_deployed = []
        if self.vlans:
            for item in self.vlans:
                id = int(item['id'])
                vlans_deployed.append(id)

        deploy_count = 0
        for vlan in vlans_to_deploy:
            id = int(vlan['id'])
            if id not in vlans_deployed:
                try:
                    apikey = config.api_key
                    networkid = netid
                    name = vlan['name']
                    vlanid = id
                    subnet = vlan['subnet']
                    mxip = vlan['applianceIp']
                    success, str = meraki.addvlan(apikey, networkid, vlanid, name, subnet,
                                                  mxip, suppressprint=True)
                    runlogs_logger.info("created vlan {}".format(id))
                    logger.info("created vlan {} netid {}".format(id, networkid))

                    self.update_single_vlan(vlan, update_all=True)
                    deploy_count += 1

                except (meraki.EmailFormatError,
                        meraki.OrgPermissionError,
                        meraki.ListError) as err:
                    logger.error("Meraki error: {} netid {}".format(err.default, vlanid))
                    runlogs_logger.error("Meraki error: {}".format(err.default))
                    exit(-1)


                except Exception as err:
                    logger.error("{}".format(err.args))
                    runlogs_logger.error("{}".format(err.args))
                    gv.fake_assert()

        if deploy_count == 0 :
            logger.info("vlans already exist - no vlans added")
            runlogs_logger.info("vlans already exist - no vlans added")
        else:
            logger.info("added a total of {} vlans".format(deploy_count))
            runlogs_logger.info("added a total of {} vlans".format(deploy_count))

    @classmethod
    def update_single_vlan(self, vlan, update_all=False):
        apikey = config.api_key
        _err = None
        vl = vlan
        networkid = vl['networkId']
        id = vl['id']
        name = vl['name']
        subnet = vl['subnet']
        applianceIp = vl['applianceIp']
        fixedipassignments = vl['fixedIpAssignments']
        vpnnatsubnet = None

        if update_all:
            dnsnameservers = vl['dnsNameservers']
            reservedipranges = vl['reservedIpRanges']
        else:
            dnsnameservers = None
            reservedipranges = None

        try:
            success, _err = meraki.updatevlan(apikey, networkid, id, name, subnet, applianceIp,
                            fixedipassignments,
                            reservedipranges,
                            vpnnatsubnet,
                            dnsnameservers)

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            logger.error("Meraki error: {}".format(err.default))
            runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)


        if not success:
            raise Exception("meraki.updatevlan failed for vlan-id {} : {}".format(id, _err))

        logger.info("updated vlan {} name: {}".format(id, name))
        runlogs_logger.info("updated vlan {} name: {}".format(id, name))
        return True


    @classmethod
    def update_vlans_list(self, vlans):
        apikey = config.api_key
        _err = None
        try:
            for vlan in vlans:
                self.update_single_vlan(vlan, update_all=True)

        except Exception as err:
            logger.error("{}".format(err.args))
            runlogs_logger.error("{}".format(err.args))
            gv.fake_assert()
            return False

        return True

    @classmethod
    def delete_vlans_list(self, vlans, netid):
        try:
            for vlanid in vlans:
                self.delete(netid, vlanid)
        except Exception as err:
            logger.error("{}".format(err.args))
            runlogs_logger.error("{}".format(err.args))
            gv.fake_assert()
            return False
        return True

    @classmethod
    def get_vlans(self, netid):
        self.vlans = None
        try:
            success, self.vlans = meraki.getvlans(config.api_key, netid)
            if not success:
                logger.error("failed netid:{} {}".format(netid, self.vlans))
                runlogs_logger.error("failed {}".format(self.vlans))
                gv.fake_assert()
            fname = "vlans_{}".format(netid)
            #json.writer(fname, self.vlans)
            logger.info("netid:{} {}".format(netid, json.make_pretty(self.vlans)))
            return self.vlans

        except (meraki.EmailFormatError,
                    meraki.OrgPermissionError,
                    meraki.ListError) as err:
            logger.error("Meraki error: {}".format(err.default))
            runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)


        except Exception as err:
            logger.error("exception failure netid:{}".format(netid, self.vlans))
            runlogs_logger.error("exception failure \n{}".format(self.vlans))
            gv.fake_assert()


    @classmethod
    def get_vlan_details(self, netid, vlanid):
        self.vlans = None
        try:
            success, details = meraki.getvlandetail(config.api_key, netid, vlanid)
            if not success:
                logger.error("failed netid:{} {}".format(netid, details))
                runlogs_logger.error("failed {}".format(details))
                gv.fake_assert()
            logger.info("netid:{} {}".format(netid, json.make_pretty(details)))
            return details

        except (meraki.EmailFormatError,
                    meraki.OrgPermissionError,
                    meraki.ListError) as err:
            logger.error("Meraki error: {}".format(err.default))
            runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)


        except Exception as err:
            logger.error("exception failure netid:{}".format(netid, self.vlans))
            runlogs_logger.error("exception failure \n{}".format(self.vlans))
            gv.fake_assert()




    """
    Used to delete the vlans for the network.
    Not in used by the current orchestration.

    """
    @classmethod
    def delete(self, netid, vlanid):
        self.vlans = None
        try:

            success, self.vlans = meraki.delvlan(config.api_key, netid, vlanid)
            if success:
                logger.info("deleted vlan {}".format(vlanid))
                runlogs_logger.info("deleted vlan {}".format(vlanid))
            else:
                logger.info("vlan does not exist vlan {} not deleted".format(vlanid))
                runlogs_logger.info("vlan does not exist vlan {} not deleted".format(vlanid))
                gv.fake_assert()
            logger.debug("netid:{} vlanid:{}".format(netid, vlanid))

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            logger.error("Meraki error: {}".format(err.default))
            runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)

        except Exception as err:
            logger.error("exception failure netid:{} - vlanid:{}".format(netid, vlanid))
            runlogs_logger.error("exception failure - vlanid {}".format(vlanid))
            gv.fake_assert()


def create_update_vlans(netid):
    """Sets vlans from a json file"""
    obj=Vlans()
    obj.create_update_vlans_list(netid)

def update_vlans(netid):
    """Sets vlans from a json file"""
    fname = "vlans_generated_{}".format(netid)
    vlans_to_deploy = json.reader(fname)

    obj=Vlans()
    obj.update_vlans_list(vlans_to_deploy)

def delete_vlans(netid, vlan_list):
    obj=Vlans()
    obj.delete_vlans_list(vlan_list, netid)

def delete(netid, vlanid):
    """Sets vlans from a json file"""
    obj=Vlans()
    obj.delete(netid, vlanid)

def get_vlans(netid):
    obj=Vlans()
    vlans = obj.get_vlans(netid)
    return vlans

def get_vlan(netid, vlanid):
    """Gets vlans for a given netid into a json file"""
    obj=Vlans()
    details = obj.get_vlan_details(netid, vlanid)
    return details


def test_create(netid):
    id=300
    apikey="5d6040171da721ec875ae2e4c42b533cb438d147"

    #def addvlan(api_key, networkid, vlanid, name, subnet, mxip, suppressprint=False):

    success, _err = meraki.addvlan(apikey, networkid=netid, vlanid=id, name="test_linus", subnet="192.168.100.0/24", mxip="192.168.100.200")

#def delvlan(api_key, networkid, vlanid, suppressprint=False):


if __name__ == '__main__':
    fname="set-vlans"
    netid = "N_686798943174005443"
    #get(netid)
    id=300
    test_create(netid)
    apikey="5d6040171da721ec875ae2e4c42b533cb438d147"
    #delete(netid, id)
    #meraki.delvlan(api_key, netid, vlanid=300, suppressprint=False)
    #success, _err = meraki.addvlan(api_key, networkid=netid, vlanid=id, name="test_linus", subnet="192.168.100.0/24", mxip="192.168.100.200")

#create(networkid)
    #delete(networkid, 1)

    netid = "N_686798943174008296"
