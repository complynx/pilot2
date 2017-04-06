#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Daniel Drizhuk, d.drizhuk@gmail.com, 2017
# - Mario Lassnig, mario.lassnig@cern.ch, 2017

import sys
import traceback
import threading

import logging
logger = logging.getLogger(__name__)


def log_exception(exception, exc_info=sys.exc_info(), level=logging.WARNING):
    '''
    Exception formatter and logger.

    Logs a caught exception into the Logger 'Exception' according to logging configs.
    Unlike python logger, this will output stack trace in the reverse way (easier to look) and with better readability.
    Also, prints out thread information, because this is very useful in massively threaded case.

    :param (Exception) exception:
    :param exc_info: Optional, the output of the `sys.exc_info()`, if it was caught earlier.
    :param level: Optional, the desired level of the logging.
    '''
    try:
        tb = list(reversed(traceback.extract_tb(exc_info[2])))

        tb_str = '\n'
        for i in tb:
            tb_str += '{file}:{line} (in {module}): {call}\n'.format(file=i[0],
                                                                     line=i[1],
                                                                     module=i[2],
                                                                     call=i[3])
        thread = threading.currentThread()
        msg = '%s: %s' % (exc_info[0].__name__, exception.message)
        msg += '\nTraceback: (latest call first)' + tb_str + 'Thread: %s(%d)' % (thread.getName(), thread.ident)

        logger.handle(logger.makeRecord(logger.name, level, tb[0][0], tb[0][1], msg, (), None, tb[0][2]))
    except Exception as e:
        logger.warn("Could not make an exception trace for exception: %s" % exception.message)
        logger.warn("Caught exeption: %s" % e.message)
