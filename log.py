
"""Log utilities"""

from time import time, strftime
import logging
logging.basicConfig(filename='swap.log', filemode='w', level=logging.DEBUG, \
format='%(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def timestamp():
	return strftime('%H:%M:%S') + "." + str(time()).split('.')[1][:2]
def DEBUG(msg, *args): logger.debug(timestamp() + " " + msg, *args)
def INFO(msg, *args): logger.info(timestamp() + " " + msg, *args)
def WARN(msg, *args): logger.warning(timestamp() + " " + msg, *args)
def ERROR(msg, *args): logger.error(timestamp() + " " + msg, *args)
