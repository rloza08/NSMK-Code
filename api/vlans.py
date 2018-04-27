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

        for item in vlans_to_deploy:
            id = int(item['id'])
            if id not in vlans_deployed:
                print ("Creating vlan : {}".format(id))
                apikey = config.api_key
                networkid = netid
                name = item['name']
                vlanid = id
                subnet = item['subnet']
                mxip = item['applianceIp']
                #apikey, networkid, vlanid, name, subnet, mxip, suppressprint = False)


                success, str = meraki.addvlan(apikey, networkid, vlanid, name, subnet, mxip, suppressprint=True)

                # l.logger.debug("create id:{} , name:{}".format(id, name))
                # if not success:
                #     l.logger.error("failed")
                #     gv.fake_assert()

        # If the vlan is not deployed create it

        self.update_vlans_list(vlans_to_deploy, netid, update_flag)

    @classmethod
    def update_vlans_list(self, vlans, netid, update_flag=True):
        apikey = config.api_key
        _err = None
        try:
            for vl in vlans:
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
                    continue

                success, _err = meraki.updatevlan(apikey, networkid, id, name, subnet, applianceIp,
                                fixedipassignments,
                                reservedipranges,
                                vpnnatsubnet,
                                dnsnameservers)

                if not success:
                    raise Exception("meraki.updatevlan failed for vlan-id {} : {}".format(id, _err))

                l.logger.debug("updatevlan :{} name:{}".format(id, name))
                l.runlogs_logger.debug("updatevlan :{} name:{}".format(id, name))

        except Exception as err:
            l.logger.error("{}".format(err.args))
            l.runlogs_logger.error("{}".format(err.args))
            gv.fake_assert()
            return False

            gv.fake_assert()
        return True

    @classmethod
    def get_vlans(self, netid):
        self.vlans = None
        try:
            success, self.vlans = meraki.getvlans(config.api_key, netid)
            if not success:
                l.logger.error("failed netid:{} {}".format(netid, self.vlans))
                l.runlogs_logger.error("failed netid:{} {}".format(netid, self.vlans))
                gv.fake_assert()
            fname = "vlans_{}".format(netid)
            #json.writer(fname, self.vlans)
            l.logger.info("netid:{} {}".format(netid, json.make_pretty(self.vlans)))
        except Exception as err:
            l.logger.error("exception failure netid:{}".format(netid))
            l.runlogs_logger.error("exception failure netid:{}".format(netid))
            gv.fake_assert()

    """
    Used to delete the vlans for the network.
    Not in used by the current orchestration.

    """
    def delete(self, netid, vlanid):
        self.vlans = None
        try:
            success, self.vlans = meraki.getvlans(config.api_key, netid)

            success, self.vlans = meraki.delvlan(config.api_key, netid, vlanid)
            if not success:
                l.logger.error("failed netid:{} vlanid:{}".format(netid, vlanid))
                l.runlogs_logger.error("failed netid:{} vlanid:{}".format(netid, vlanid))
                gv.fake_assert()
            l.logger.debug("netid:{} vlanid:{}".format(netid, vlanid))
        except Exception as err:
            l.logger.error("exception failure netid:{} vlanid:{}".format(netid, vlanid))
            l.runlogs_logger.error("exception failure netid:{} vlanid:{}".format(netid, vlanid))
            gv.fake_assert()


def get(netid):
    """Gets vlans for a given netid into a json file"""
    obj=Vlans()
    obj.get(netid)

def create_update_vlans_list(netid):
    """Sets vlans from a json file"""
    obj=Vlans()
    obj.create_update_vlans_list(netid)

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
