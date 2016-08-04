#!/usr/bin/env python

import yaml
import os
import logging
from modules.security import motion_detection

cwd = os.path.dirname(os.path.realpath(__file__))
config = yaml.load(file('%s/config/config.yml'%cwd, 'r'))

logging.basicConfig(format=config['log_format'])
logger = logging.getLogger(__name__)
logger.setLevel(config['log_level'])

class houston(object):
  def __init__(self):
    logger.info("starting %s"%__name__)
    motiondetection = motion_detection

if __name__ == '__main__':
  houston()
