import logging
import datetime
import global_vars as gv
import os
if not os.path.exists("../../data/logs"):
    os.makedirs("../../data/logs")

logger = None
runlogs_logger = None
runlogs_logger = None
runlogs_logger = None
module_setup_done = False



#config = json_reader("../config/safeway-utils.json")

if gv.log_verbose:
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
    global logger, runlogs_logger, runlogs_logger, runlogs_logger
    if not module_setup_done:
        now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        fulllog_file = "../../data/logs/debug_{}.log".format(now)
        fulllog_file = fulllog_file.replace(":", "-")
        fulllog_file = fulllog_file.replace(" ", "-")
        fulllog_file = fulllog_file.replace("_", "-")

        runlog_file = "../../data/logs/run_{}.log".format(now)
        runlog_file = runlog_file.replace(":", "-")
        runlog_file = runlog_file.replace(" ", "-")
        runlog_file = runlog_file.replace("_", "-")


        debug_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s', "%Y-%m-%d %H:%M:%S ")

        light_formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S ")

        if logging_debug_level == "debug":
            light_formatter = debug_formatter

        # first file logger
        logger = setup_logger("nxmk", log_file=fulllog_file, level=logging.DEBUG, formatter=debug_formatter)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(light_formatter)


        ## Send VERBOSE to console
        if logging_debug_level == "debug":
            logger.addHandler(consoleHandler)

        runlogs_formatter = light_formatter
        if os.path.isfile("../../data/logs/runlogs.log"):
            os.unlink("../../data/logs/runlogs.log")

        runlogs_logger = setup_logger('nxmk_runlogs', log_file=runlog_file, level=logging.DEBUG,
                                       formatter= runlogs_formatter)
        runlogs_logger.addHandler(consoleHandler)



def message_user(str):
    global runlogs_logger
    print (str)
    print ("_" * 72)
    #sys.stdout.flush()

def __main__():
   setup()
   runlogs_logger.info('Inside method')
   runlogs_logger.info('Inside method')
   logger.info('Inside method')
