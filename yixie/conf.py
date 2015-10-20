#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import logging.handlers

def config_logger():
    """配置logging的日志文件以及日志的记录等级
    """

    log = logging.getLogger("aixie")
    log.setLevel(logging.DEBUG)
    file_handler = logging.handlers.TimedRotatingFileHandler('yixie-time.log', when='H', interval=1, backupCount=40)
    file_handler.setLevel(logging.INFO)
    # 2014-07-06 23:47:34
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s",
            '%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    """

    debug_handler = logging.FileHandler("etdown-admin.log")
    debug_handler.setLevel(logging.ERROR)
    #debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d %(funcName)s] %(levelname)s [%(threadName)s] %(message)s", '%Y-%m-%d %H:%M:%S')
    debug_handler.setFormatter(debug_formatter)
    log.addHandler(debug_handler)
    """
