import logging
import os
import datetime
import global_vars
import sys

logger = None
firewall_logger = None
vpn_firewall_logger = None
store_orchestration_logger = None
module_setup_done = False


#config = json_reader("../config/safeway-utils.json")

if global_vars.log_verbose:
    logging_debug_level = "debug"
else:
    logging_debug_level = "info"

def setup_logger(name, log_file, level=logging.INFO, formatter=None):
    """Function setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def setup():
    global module_setup_done
    global logger, firewall_logger, vpn_firewall_logger, store_orchestration_logger
    if not module_setup_done:
        now = datetime.datetime.now()
        logfile = os.environ.get("NSMK_LOGFILE", "../data/nsmk_automation_{}.log".format(now))
        if os.name == 'nt':
            logfile = logfile.replace(":", "_")
        debug_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')

        light_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s",
                                      "%Y-%m-%d %H:%M:%S ")


        if logging_debug_level == "debug":
            light_formatter = debug_formatter

        # first file logger
        logger = setup_logger("nxmk_backend", log_file=logfile, level=logging.DEBUG, formatter=debug_formatter)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(light_formatter)


        ## Send VERBOSE to console
        if logging_debug_level == "debug":
            logger.addHandler(consoleHandler)

        firewall_formatter = light_formatter
        if os.path.isfile("../firewall.log"):
            os.unlink("../firewall.log")
        logfile='../firewall.log'
        firewall_logger = setup_logger('nxmk_firewall', '../firewall.log', level=logging.DEBUG,
                                       formatter= firewall_formatter)
        firewall_logger.addHandler(consoleHandler)
        if os.path.isfile("../vpn_firewall.log"):
            os.unlink("../vpn_firewall.log")
        logfile='../s2svpnfw_rules.log'
        vpn_firewall_logger = setup_logger('nxmk_vpn_firewall', log_file=logfile, level=logging.DEBUG,
                            formatter = light_formatter)
        vpn_firewall_logger.addHandler(consoleHandler)

        store_orchestration_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        if os.path.isfile("../store_orchestration.log"):
            os.unlink("../store_orchestration.log")
        store_orchestration_logger = setup_logger('nxmk_store_orchestration', '../store_orchestration.log', level=logging.DEBUG,
                                       formatter= store_orchestration_formatter)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(light_formatter)
        store_orchestration_logger.addHandler(consoleHandler)


def message_user(str):
    global firewall_logger
    print (str)
    print ("_" * 72)
    #sys.stdout.flush()

def __main__():
   setup()
   firewall_logger.info('Inside method')
   vpn_firewall_logger.info('Inside method')
   logger.info('Inside method')
