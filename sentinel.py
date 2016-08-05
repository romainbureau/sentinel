#!/usr/bin/env python

import yaml
import os
import logging
import time
import sys
import argparse

from multiprocessing import Process, Queue

from modules.security import motion_detection
from lib.event_listener import event_listener
from lib.http_server import http_server
from lib.rtsp_server import rtsp_server

def argv_parser(argv):
    """ parse commandline argument """
    parser = argparse.ArgumentParser(prog=__file__, usage='%(prog)s [options]')
    parser.add_argument('-e', '--env', required=True)

    return parser.parse_args(argv)

args = argv_parser(sys.argv[1:])

cwd = os.path.dirname(os.path.realpath(__file__))
config = yaml.load(file('%s/config/config_%s.yml'%(cwd, args.env), 'r'))

logging.basicConfig(format=config['log_format'])
logger = logging.getLogger('sentinel')
logger.setLevel(config['log_level'])

class sentinel(object):
  def __init__(self):
    processes = []
    events_queue = Queue(config['events_queue_size'])
    logger.info("starting")

    rtsp = Process(target=rtsp_server, args=(config["rtsp_server"], ))
    processes.append(rtsp)

    http = Process(target=http_server, args=(config, events_queue, ))
    processes.append(http)

    md = Process(target=motion_detection.motion_detection, args=(config, events_queue, ))
    processes.append(md)

    el = Process(target=event_listener, args=(config, events_queue, ))
    processes.append(el)

    for process in processes:
      process.start()

    for process in processes:
      process.join()

    for process in processes:
      process.terminate()

if __name__ == '__main__':
  try:
    h = sentinel()
  except (KeyboardInterrupt, SystemExit):
    logger.info("stopping")
    time.sleep(1)
