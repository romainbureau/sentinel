#!/usr/bin/env python

from datetime import datetime
import os
import cv2
import logging

logger = logging.getLogger('sentinel')

class save_picture(object):

  def __init__(self, basedir, dateformat="%Y/%m/%d/%H"):
    self.basedir = basedir
    date = datetime.now().strftime(dateformat)
    self.path = '/'.join([basedir, date])
    if not os.path.isdir(self.path):
      logger.info("create dir: %s"%self.path)
      os.makedirs(self.path)

  def save(self, filename, payload):
    filepath = '/'.join([self.path, filename])
    logger.info("save image to %s"%filepath)
    cv2.imwrite(filepath, payload)
    return filepath

