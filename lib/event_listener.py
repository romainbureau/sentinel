#!/usr/bin/env python

import logging
from datetime import datetime
import time
from lib.sendmail import sendmail
from email.mime.image import MIMEImage
from lib.save_picture import save_picture
import os

logger = logging.getLogger("sentinel")

class event_listener(object):

  def __init__(self, config, events_queue):
    logger.info("starting event listener")
    self.config = config
    self.events_queue = events_queue

    self.last_event_ts = int(time.time())
    self.terminated = False
    self.mute_ts = self.last_event_ts
    try:
      while not self.terminated:
        if not events_queue.empty():
          ts = int(time.time())
          message = events_queue.get()
          logger.info("%s: %s", message.get_event_type(), message.get_content())
          if message.get_event_type() == "motion":
            self.motion_message(message, ts)
          self.last_event_ts = ts
        else:
          time.sleep(0.20)
    except (KeyboardInterrupt, SystemExit):
      logger.info("stopping event listener")
      self.terminated = True

  def motion_message(self, message, ts):
    # event_type = message.get_event_type()
    content = message.get_content()
    status_file = self.config["motion_detection"]["status_file"]%"disable"
    if content == "enable":
      if os.path.isfile(status_file):
        os.remove(status_file)
    elif content == "disable":
      f = open(status_file,'w')
      f.write("1")
      f.close()
    else:
      if ts > self.mute_ts:
        sm = sendmail(self.config['smtp'])
        sp = save_picture(self.config['motion_detection']['save_dir'])

        self.mute_ts = ts + self.config['mute_seconds']
        sm.set_message(self.config['email'], "motion detection at %s"%datetime.now().strftime("%A %d %B %Y %H:%M:%S"), "hostname: %s"%os.uname()[1])
        filename = sp.save("%s.jpg"%ts, message.get_payload())
        filecontent = open(filename, 'rb')
        part = MIMEImage(filecontent.read(), name=os.path.basename(filename))
        filecontent.close()
        sm.set_attachment(part)
        sm.send()

