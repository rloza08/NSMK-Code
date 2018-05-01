#!/usr/bin/env python3
import utils.auto_config as config
import utils.auto_logger as l
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
            if not success:
                l.logger.error("{}".format(str))
                l.runlogs_logger.error("{}".format(str))
                gv.fake_assert()

        except (meraki.EmailFormatError,
                meraki.OrgPermissionError,
                meraki.ListError) as err:
            l.logger.error("Meraki error: {}".format(err.default))
            l.runlogs_logger.error("Meraki error: {}".format(err.default))

        except Exception as err:
            l.logger.error("exception failure netid:{}\n{}".format(netid, str))
            l.runlogs_logger.error("exception failure netid:{}\n{}".format(netid, str))
            gv.fake_assert()

        return success, str


def add_static_route(netid, name, subnet, ip):
    StaticRoute.add(netid, name, subnet, ip)


if __name__ == '__main__':
    pass
