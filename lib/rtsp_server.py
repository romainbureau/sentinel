#!/usr/bin/env python

import subprocess
import logging
import os

logger = logging.getLogger("sentinel")


class rtsp_server(object):

  def __init__(self, config):
    cmd = [config["bin"]]
    cmd.append("-F %d"%config["framerate"])
    cmd.append("-W %d"%config["width"])
    cmd.append("-H %d"%config["height"])
    cmd.append("-P %d"%config["port"])
    cmd.append(config["dev"])

    FNULL = open(os.devnull, 'w')
    logger.info(' '.join(cmd))
    subprocess.call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)

