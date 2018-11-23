import numpy as np

"""
Holds stigmergy information for a link.
Not really used currently.
"""
class Cache:

  def __init__(self, env, l):
    self.env = env
    self.l = l
    self.short = l
    self.long = l
    self.anticip = 0
    self.buffer = []
    self.short_start_index = 0

  def store_data(self, travel_time):
    self.buffer.append(travel_time)
    print(self.buffer)

  def __update_short_term_stigmergy(self):
    data = np.array(self.buffer[self.short_start_index:])
    self.short_start_index = len(self.buffer)
    
    self.short = data.mean() if len(data) > 0 else self.l

  def __update_long_term_stigmergy(self):
    data = np.array(self.buffer)
    self.buffer = []
    self.short_start_index = 0

    self.long = data.mean() + 0.05 * data.std() if len(data) > 0 else self.l

  # TODO
  def __update_anticipatory_stigmergy(self):
    return []

  def update_stigmery(self):
    i = 0
    while True:
      yield self.env.timeout(5)
      i += 5

      self.__update_short_term_stigmergy()

      # long term stigmergy updated every 24h (1440 minutes in one day)
      if i % 1440 == 0:
        self.__update_long_term_stigmergy()