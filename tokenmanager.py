import os
import time
import logging

class TokenManager:
  def __init__(self, update_interval_s):
    self.update_interval_s = update_interval_s
    self.last_update = 0

  def updateTokens(self):
    logging.debug("Updating tokens")
    ret = os.system('kinit -R && aklog')
    self.last_update = time.time()
    if ret != 0:
      logging.critical("Token update failed: %s" % ret)
    return ret

  def updateTokensIfNecessary(self):
    if self.update_interval_s < 0:
      return 1

    if time.time() - self.last_update > self.update_interval_s:
      return updateTokens()
    else:
      return 0

