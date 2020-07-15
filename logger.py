#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from colorlog import ColoredFormatter

# Logger usage:
# log.info('string')
# log.debug('string')
# log.warning('string')
# log.error('string')
# log.critical('string')
LOG_LEVEL = logging.DEBUG
LOGFORMAT = ' %(log_color)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)
log.propagate = False


