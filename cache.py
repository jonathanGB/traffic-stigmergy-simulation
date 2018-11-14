
"""
Holds stigmergy information for a link.
Not really used currently.
"""
class Cache:

  def __init__(self):
    self.short = None
    self.long = None
    self.anticip = None

  def get_short(self):
    return self.short

  def get_long(self):
    return self.long

  def get_anticip(self):
    return self.anticip

  def set_short(self, short):
    self.short = short

  def set_long(self, long):
    self.long = long

  def set_anticip(self, anticip):
    self.anticip = anticip