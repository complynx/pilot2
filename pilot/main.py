#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Daniel Drizhuk, d.drizhuk@gmail.com, 2017

import sys
import argparse
import logging

from util import signalslot, https
from util.config import config
from util.signalslot import Signal
from control.queue import Queue
from control.job import Job

VERSION = '2017-07-18.001 dan'


class Pilot(signalslot.Signaller):
    arg_parser = None
    args = None
    config = None
    ready_get_job = Signal()
    queue = None
    job = None

    def __init__(self):
        super(Pilot, self).__init__()
        self.set_arguments()

    def set_arguments(self):
        arg_parser = argparse.ArgumentParser()

        arg_parser.add_argument('-d',
                                dest='debug',
                                action='store_true',
                                default=False,
                                help='enable debug logging messages')

        # the choices must match in name the python module in pilot/workflow/
        arg_parser.add_argument('-w',
                                dest='workflow',
                                default='generic',
                                choices=['generic', 'generic_hpc',
                                         'production', 'production_hpc',
                                         'analysis', 'analysis_hpc',
                                         'eventservice', 'eventservice_hpc'],
                                help='pilot workflow (default: generic)')

        # graciously stop pilot process after hard limit
        arg_parser.add_argument('-l',
                                dest='lifetime',
                                default=10,
                                type=int,
                                help='pilot lifetime seconds (default: 10)')

        # set the appropriate site and queue
        arg_parser.add_argument('-q',
                                dest='queue',
                                required=True,
                                help='MANDATORY: queue name (e.g., AGLT2_TEST-condor')

        arg_parser.add_argument('-j',
                                dest='job_label',
                                default='ptest_d',
                                help='job prod/source label (default: ptest_d)')

        # SSL certificates
        arg_parser.add_argument('--cacert',
                                dest='cacert',
                                default=None,
                                help='CA certificate to use with HTTPS calls to server, commonly X509 proxy',
                                metavar='path/to/your/certificate')
        arg_parser.add_argument('--capath',
                                dest='capath',
                                default=None,
                                help='CA certificates path',
                                metavar='path/to/certificates/')

        arg_parser.add_argument('--config',
                                dest='config',
                                default='',
                                help='Pilot configuration file',
                                metavar='path/to/pilot_conf.json')

        self.arg_parser = arg_parser

    def setup(self):
        config.read(self.args.config)
        self.set_logging()
        https.https_setup(self.args, VERSION)

    def set_logging(self):
        console = logging.StreamHandler(sys.stdout)
        if self.args.debug:
            logging.basicConfig(filename='pilotlog.txt', level=logging.DEBUG,
                                format='%(asctime)s | %(levelname)-8s | %(threadName)-10s | %(name)-32s | %(funcName)-32s | %(message)s')
            console.setLevel(logging.DEBUG)
            console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(threadName)-10s | %(name)-32s | %(funcName)-32s | %(message)s'))
        else:
            logging.basicConfig(filename='pilotlog.txt', level=logging.INFO,
                                format='%(asctime)s | %(levelname)-8s | %(message)s')
            console.setLevel(logging.INFO)
            console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s'))
        logging.getLogger('').addHandler(console)

    def run(self, argv=sys.argv):
        self.args = self.arg_parser.parse_args(argv[1:])
        self.setup()

        self.queue = Queue()
        self.ready_get_job.connect(self.queue.get_job)
        self.queue.got_job.connect(self.on_got_job)

        self.ready_get_job()

    def on_got_job(self, job_res):
        self.job = Job(job_res)

