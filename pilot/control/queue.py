#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Daniel Drizhuk, d.drizhuk@gmail.com, 2017

from pilot.util.signalslot import Signaller, Signal
from pilot.util.async import async
from pilot.util import https
from pilot import pilot
from pilot import config

import logging
logger = logging.getLogger(__name__)


class Queue(Signaller):
    got_job = Signal()

    def __init__(self):
        super(Queue, self).__init__()

    @async
    def get_job(self):
        logger.debug('trying to fetch job')

        data = {'siteName': pilot.args.queue,
                'prodSourceLabel': pilot.args.job_label}

        res = https.request('https://{pandaserver}/server/panda/getJob'.format(pandaserver=config.Pilot.pandaserver),
                            data=data)

        if res is None:
            logger.warning('did not get a job -- sleep 1000s and repeat')
        else:
            if res['StatusCode'] != 0:
                logger.warning('did not get a job -- sleep 1000s and repeat -- status: %s' % res['StatusCode'])
            else:
                logger.info('got job: %s -- sleep 1000s before trying to get another job' % res['PandaID'])
                self.got_job(res)
