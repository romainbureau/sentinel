#!/usr/bin/env python

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logger = logging.getLogger('sentinel')

class sendmail(object):
  def __init__(self, config):
    self.config = config
    self.msg = None

    if not self.config['mute_email']:
      try:
        self.server = smtplib.SMTP(config['host'], config['port'])
        self.server.starttls()
        self.server.login(config['username'], config['password'])
      except Exception as err:
        logger.error("cannot connect to smtp server: %s"%err)

  def set_attachment(self, part):
    if self.msg == None:
      raise RuntimeError('you should set_message before sending')
    self.msg.attach(part)

  def set_message(self, to, subject, message, attachment = None):
    self.msg = MIMEMultipart()
    self.msg['From'] = self.config['username']
    self.msg['To'] = to
    self.msg['Subject'] = subject
    self.msg.attach(MIMEText(message))

  def send(self):
    try:
      if self.msg == None:
        raise RuntimeError('you should set_message before sending')
      logger.info("sending email, <from: %s> <to: %s> with <subject: %s>"%(self.msg['From'], self.msg['To'], self.msg['Subject']))
      if not self.config['mute_email']:
        self.server.sendmail(self.msg['From'], self.msg['To'], self.msg.as_string())

        self.server.quit()
    except Exception as err:
      logger.error("cannot send email: %s"%err)

