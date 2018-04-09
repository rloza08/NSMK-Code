#!/usr/bin/env python3
import json
import utils.auto_logger as l
import traceback
import utils.auto_utils as utils
import os
from global_vars import log_verbose as l_verbose

class Json:
    @classmethod
    def make_pretty(self, my_json):
        return (json.dumps(my_json, indent=4, sort_keys=False))

    @classmethod
    def writer_full_path(self, fname, data):
        str = self.make_pretty(data)
        try:
            with open(fname, 'w') as f:
                json_data=f.write(str)
        except Exception as err:
            l.logger.error("failure")
            l.store_orchestration_logger.error("failure")
            if l_verbose:
               traceback.print_tb(err.__traceback__)
               assert(0)
            exit(-1)

    @classmethod
    def writer(self, fname, data, path="data", absolute_path=None):
        fnameJson = utils.get_path(fname, path, "json")
        self.writer_full_path(fnameJson, data)

    @classmethod
    def reader(self, fname, path="data"):
        data = None
        try :
            fnameJson = utils.get_path(fname, path, "json")
            json_data=open(fnameJson).read()
            # json_data = json_data.replace("\n","")
            data = json.loads(json_data)
            #l.logger.debug("data: {}".format(data))
        except Exception as err:
            l.logger.error("fname:{} {}".format(fname, fnameJson))
            l.store_orchestration_logger.error("DEPLOY ... fname:{} {}".format(fname, fnameJson))
            if l_verbose:
                traceback.print_tb(err.__traceback__)
                assert(0)

            os._exit(-1)
        return data

