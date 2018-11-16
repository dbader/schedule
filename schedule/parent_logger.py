#!/usr/bin/env python
# coding: utf-8

import time, logging

def setup_logging(debug):
    if debug:
        log_level = logging.getLevelName('DEBUG')
    else:
        log_level = logging.getLevelName('INFO')

    logging.basicConfig(level=log_level,
                        format="%(asctime)s %(name)s[%(process)d] %(levelname)s - %(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S UTC',
                        filename='/var/log/schedule.log')

    # BUG: this does not print the TZ name because logging module is stupid...
    logging.Formatter.converter = time.gmtime

    #global logger
    #logger = logging.getLogger("confd")

