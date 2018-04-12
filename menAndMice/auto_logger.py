# Add environment variables driven customizatio
import logging
import os
import datetime


LOGSCREEN=os.environ.get("MKLOG_SCREEN","SCREEN")
LOGLEVEL=os.environ.get("MKLOG_LEVEL","DEBUG")

now = datetime.datetime.now()
LOGFILE=os.environ.get("MKLOG_FILE","../../data/meraki_auto_{}.log".format(now))
if os.name == 'nt':
	LOGFILE=LOGFILE.replace(":","_")

logger = logging.getLogger('auto-meraki')
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')

if LOGFILE:
	fileHandler = logging.FileHandler("{}".format(LOGFILE))
	fileHandler.setFormatter(formatter)
	logger.addHandler(fileHandler)

if LOGSCREEN:
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(formatter)
	logger.addHandler(consoleHandler)

if LOGLEVEL == "ERROR":
	logger.setLevel(logging.ERROR)
elif LOGLEVEL == "WARNING":
	logger.setLevel(logging.WARNING)
elif LOGLEVEL == "INFO":
	logger.setLevel(logging.INFO)
elif LOGLEVEL == "DEBUG":
	logger.setLevel(logging.DEBUG)
