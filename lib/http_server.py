#!/usr/bin/env python

from flask import Flask, render_template, Response, send_file
import logging
from lib.message import message
import cv2

logger = logging.getLogger('sentinel')

class http_server(object):
  def __init__(self, config, events_queue):
    logger.info("starting http server")
    self.events_queue = events_queue
    self.config = config
    self.app = Flask("sentinel")
    self.app.use_reloader=False
    self.start()

  def index(self):
    return "ok"

  def start(self):
    self.app.add_url_rule('/', view_func=self.video)
    self.app.add_url_rule('/snapshot', view_func=self.snapshot)
    self.app.add_url_rule('/motion_detection/<status>', view_func=self.motion_detection)
    self.app.run(host=self.config["http_host"], port=self.config["http_port"], debug=self.config["http_debug"], use_reloader=False)

  def snapshot(self):
    msg = message()
    msg.set_event_type("snapshot")
    msg.set_content("asked from http")
    self.events_queue.put(msg)

    return "ok"

  def motion_detection(self, status):
    if status in ["disable", "enable"]:
      msg = message()
      msg.set_event_type("motion")
      msg.set_content(status)
      self.events_queue.put(msg)
      return "ok"
    else:
      logger.error("unkown action %s"%status)
      return "ko", HTTP_400_BAD_REQUEST

  def video(self):
    video = cv2.VideoCapture(self.config['video_resource'])
    ret, frame = video.read()
    if ret:
      cv2.imwrite("/tmp/snapshot.jpeg", frame)
    return send_file("/tmp/snapshot.jpeg", mimetype='image/jpeg')
