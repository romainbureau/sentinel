#!/usr/bin/env python

class message(object):
  def __init__(self):
    self.event_type = None
    self.content = None
    self.payload = None
    self.allowed_event_types = ["motion"]

  def set_event_type(self, event_type):
    if event_type in self.allowed_event_types:
      self.event_type = event_type
    else:
      raise InvalidArgumentException("unknown event type: %s"%event_type)

  def get_event_type(self):
    return self.event_type

  def set_content(self, content):
    self.content = content

  def get_content(self):
    return self.content

  def set_payload(self, payload):
    self.payload = payload

  def get_payload(self):
    return self.payload
