#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_json as json
import utils.auto_logger as l
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
                    l.logger.info("created vlan {}".format(id))
                    l.runlogs_logger.info("created vlan {} netid {}".format(id, networkid))

                    self.update_single_vlan(vlan, netid, update_flag)
                    deploy_count += 1

                except (meraki.EmailFormatError,
                        meraki.OrgPermissionError,
                        meraki.ListError) as err:
                    l.logger.error("Meraki error: {} netid {}".format(err.default, vlanid))
                    l.runlogs_logger.error("Meraki error: {}".format(err.default))
                    exit(-1)


                except Exception as err:
                    l.logger.error("{}".format(err.args))
                    l.runlogs_logger.error("{}".format(err.args))
                    gv.fake_assert()

        if deploy_count == 0 :
            l.logger.info("vlans already exist - no vlans added")
            l.runlogs_logger.info("vlans already exist - no vlans added")
        else:
            l.logger.info("added a total of {} vlans".format(deploy_count))
            l.runlogs_logger.info("added a total of {} vlans".format(deploy_count))

    @classmethod
    def update_single_vlan(self, vlan, netid, update_flag=True):
        apikey = config.api_key
        _err = None
        vl = vlan
        networkid = vl['networkId']
        id = vl['id']
        name = vl['name']
        subnet = vl['subnet']
        applianceIp = vl['applianceIp']
        fixedipassignments = vl['fixedIpAssignments']
        reservedipranges = vl['reservedIpRanges']
        vpnnatsubnet = None
        dnsnameservers = vl['dnsNameservers']
        performUpdate = (fixedipassignments or \
                         reservedipranges or \
                         vpnnatsubnet or \
                         dnsnameservers) is not None

        if performUpdate is False:
            return True
        try:
            success, _err = meraki.updatevlan(apikey, networkid, id, name, subnet, applianceIp,
                            fixedipassignments,
                            reservedipranges,
                            vpnnatsubnet,
                            dnsnameservers)

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            l.logger.error("Meraki error: {}".format(err.default))
            l.runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)


        if not success:
            raise Exception("meraki.updatevlan failed for vlan-id {} : {}".format(id, _err))

        l.logger.info("updated vlan {} name: {}".format(id, name))
        l.runlogs_logger.info("updated vlan {} name: {}".format(id, name))
        return True


    @classmethod
    def update_vlans_list(self, vlans, netid, update_flag=True):
        apikey = config.api_key
        _err = None
        try:
            for vlan in vlans:
                self.update_single_vlan(vlan, netid, update_flag)

        except Exception as err:
            l.logger.error("{}".format(err.args))
            l.runlogs_logger.error("{}".format(err.args))
            gv.fake_assert()
            return False

        return True

    @classmethod
    def delete_vlans_list(self, vlans, netid):
        try:
            for vlanid in vlans:
                self.delete(netid, vlanid)
        except Exception as err:
            l.logger.error("{}".format(err.args))
            l.runlogs_logger.error("{}".format(err.args))
            gv.fake_assert()
            return False
        return True

    @classmethod
    def get_vlans(self, netid):
        self.vlans = None
        try:
            success, self.vlans = meraki.getvlans(config.api_key, netid)
            if not success:
                l.logger.error("failed netid:{} {}".format(netid, self.vlans))
                l.runlogs_logger.error("failed {}".format(self.vlans))
                gv.fake_assert()
            fname = "vlans_{}".format(netid)
            #json.writer(fname, self.vlans)
            l.logger.info("netid:{} {}".format(netid, json.make_pretty(self.vlans)))

        except (meraki.EmailFormatError,
                    meraki.OrgPermissionError,
                    meraki.ListError) as err:
            l.logger.error("Meraki error: {}".format(err.default))
            l.runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)


        except Exception as err:
            l.logger.error("exception failure netid:{}".format(netid, self.vlans))
            l.runlogs_logger.error("exception failure \n{}".format(self.vlans))
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
                l.logger.info("deleted vlan {}".format(vlanid))
                l.runlogs_logger.info("deleted vlan {}".format(vlanid))
            else:
                l.logger.info("vlan does not exist vlan {} not deleted".format(vlanid))
                l.runlogs_logger.info("vlan does not exist vlan {} not deleted".format(vlanid))
                gv.fake_assert()
            l.logger.debug("netid:{} vlanid:{}".format(netid, vlanid))

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            l.logger.error("Meraki error: {}".format(err.default))
            l.runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)

        except Exception as err:
            l.logger.error("exception failure netid:{} - vlanid:{}".format(netid, vlanid))
            l.runlogs_logger.error("exception failure - vlanid {}".format(vlanid))
            gv.fake_assert()


def get(netid):
    """Gets vlans for a given netid into a json file"""
    obj=Vlans()
    obj.get(netid)

def create_update_vlans(netid):
    """Sets vlans from a json file"""
    obj=Vlans()
    obj.create_update_vlans_list(netid)

def update_vlans(netid):
    """Sets vlans from a json file"""
    fname = "vlans_generated_{}".format(netid)
    vlans_to_deploy = json.reader(fname)

    obj=Vlans()
    obj.update_vlans_list(vlans_to_deploy, netid)

def delete_vlans(netid, vlan_list):
    obj=Vlans()
    obj.delete_vlans_list(vlan_list, netid)

def delete(netid, vlanid):
    """Sets vlans from a json file"""
    obj=Vlans()
    obj.delete(netid, vlanid)

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
