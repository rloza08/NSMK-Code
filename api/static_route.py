#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_logger as log
import api.meraki as meraki
import global_vars as gv

"""
This call provides a wrapper to the meraki add static route

"""

class StaticRoute(object):
    @classmethod
    def add(self, netid, name, subnet, ip):
        success = False
        str = None
        try:
            success, str = meraki.addstaticroute(config.api_key, netid, name, subnet, ip)
            log.logger.info("success {}".format(str))
            if not success:
                log.logger.error("{}".format(str))
                log.runlogs_logger.error("{}".format(str))
                gv.fake_assert()

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            log.logger.error("Meraki error: {}".format(err.default))
            log.runlogs_logger.error("Meraki error: {}".format(err.default))
            exit(-1)

        except Exception as err:
            log.logger.error("exception failure {} for netid:{} \n{}".format(netid, err, str))
            log.runlogs_logger.error("exception failure {} \n{}".format(err, str))
            gv.fake_assert()

        return success, str


def add_static_route(netid, name, subnet, ip):
    StaticRoute.add(netid, name, subnet, ip)


if __name__ == '__main__':
    pass
