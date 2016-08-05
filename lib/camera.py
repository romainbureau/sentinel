#!/usr/bin/env python

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import logging

logger = logging.getLogger('sentinel')

class camera(object):

  def __init__(self, config, frame_queue):
    logger.info("starting camera stream")
    self.config = config
    self.frame_queue = frame_queue
    self.resolution = (self.config['camera_resolution_width'], self.config['camera_resolution_height'])
    self.camera = PiCamera()
    self.camera.resolution = self.resolution
    self.camera.framerate = self.config['camera_framerate']
    self.camera.rotation = self.config['camera_rotation']
    self.camera.led = False
    self.rawCapture = PiRGBArray(self.camera, size=self.resolution)
    self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
    self.terminated = False
    try:
      self.start()
    except (KeyboardInterrupt, SystemExit):
      logger.info("stopping camera stream")
      self.terminated = True

  def start(self):
    for f in self.stream:
      frame = f.array
      self.frame_queue.put(frame)
      self.rawCapture.truncate(0)
      if self.terminated:
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()
        break

