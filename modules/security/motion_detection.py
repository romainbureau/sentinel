#!/usr/bin/env python

import cv2
import datetime
import imutils
import time
from lib.message import message
import logging
import os

logger = logging.getLogger('sentinel')

class motion_detection(object):

  def __init__(self, config, events_queue):
    logger.info("starting motion detection")
    self.config = config
    self.motion_detection_config = config['motion_detection']
    self.events_queue = events_queue
    self.terminated = False
    self.disabled = self.is_disabled()
    try:
      self.start()
    except (KeyboardInterrupt, SystemExit):
      logger.info("stopping motion detection")
      self.terminated = True

  def prepare_frame(self, frame):
      gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

      return gray_frame

  def motion_detection(self, frame1, frame2):
    cv2.accumulateWeighted(frame1, frame2, 0.5)
    frame_delta = cv2.absdiff(frame1, cv2.convertScaleAbs(frame2))
    thresh = cv2.threshold(frame_delta, self.motion_detection_config['delta_thresh'], 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    return thresh

  def draw_frame(self, thresh, frame):
    is_motion = False
    (contours, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
      if cv2.contourArea(contour) < self.motion_detection_config['min_area']:
        continue
      (x, y, w, h) = cv2.boundingRect(contour)
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
      is_motion = True
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%A %d %B %Y %H:%M:%S")
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.35, (0, 0, 255), 1)
    if is_motion:
      cv2.putText(frame, "motion detected", (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
    else:
      cv2.putText(frame, "ok", (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 2)

    if is_motion:
      msg = message()
      msg.set_event_type("motion")
      msg.set_content("motion detected")
      msg.set_payload(frame)
      self.events_queue.put(msg)

    return frame

  def is_disabled(self):
    status_file = self.motion_detection_config["status_file"]%"disable"
    if os.path.isfile(status_file):
      self.disabled = True
    else:
      self.disabled = False

  def start(self):
    avg = None
    time.sleep(3)
    while not self.terminated:
      if self.disabled:
        time.sleep(2)
        self.is_disabled()
      else:
        video = cv2.VideoCapture(self.config['video_resource'])
        while not self.terminated and not self.disabled:
          ret, frame = video.read()
          if ret:
            frame = imutils.resize(frame, width=400)
            gray_frame = self.prepare_frame(frame)
            text = "ok"

            if avg is None:
              avg = gray_frame.copy().astype("float")
              continue

            thresh = self.motion_detection(gray_frame, avg)
            frame = self.draw_frame(thresh, frame)

            if self.motion_detection_config['show_video']:
              cv2.namedWindow("Motion detection", cv2.WND_PROP_FULLSCREEN)
              cv2.setWindowProperty("Motion detection", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
              cv2.imshow("Motion detection", frame)
              key = cv2.waitKey(1) & 0xFF
          self.is_disabled()

        video.release()
