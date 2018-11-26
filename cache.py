import numpy as np

"""
Holds stigmergy information for a link.
"""
class Cache:

  def __init__(self, env, l):
    self.env = env
    self.l = l
    self.short = l
    self.long = l
    self.anticip = []
    self.buffer = []
    self.short_start_index = 0
    self.anticip_buffer = {}
    self.clock = 0

  def get_short_term_stigmergy(self):
    return self.short

  def get_long_term_stigmergy(self):
    return self.long

  # len(self.anticip) is `Vol(l)`
  def get_anticip_stigmergy(self):
    return len(self.anticip), self.anticip

  def store_data(self, travel_time):
    self.buffer.append(travel_time)

  def __update_short_term_stigmergy(self):
    data = np.array(self.buffer[self.short_start_index:])
    self.short_start_index = len(self.buffer)
    
    self.short = data.mean() if len(data) > 0 else self.l

  def __update_long_term_stigmergy(self):
    data = np.array(self.buffer)
    self.buffer = []
    self.short_start_index = 0

    self.long = data.mean() + 0.05 * data.std() if len(data) > 0 else self.l

  # Updates anticipatory stigmergy with a reference to a car that should be on this link
  # within `time_delta` (smaller than 10 minutes).
  def increment_anticip_stigmergy(self, car, time_delta):
    if (self.clock+time_delta) in self.anticip_buffer:
      anticip_state = self.anticip_buffer[self.clock+time_delta]
      anticip_state.append(car)
    else:
      self.anticip_buffer[self.clock+time_delta] = [car]

  def update_stigmery(self):
    while True:
      yield self.env.timeout(1)
      self.clock += 1

      # short-term stigmergy updated every 5 minutes
      if self.clock % 5 == 0:
        self.__update_short_term_stigmergy()

      # long term stigmergy updated every 24h (1440 minutes in one day)
      if self.clock % 1440 == 0:
        self.__update_long_term_stigmergy()

      # clean-up anticipatory data older than 10 minutes
      if self.clock in self.anticip_buffer:
        del self.anticip_buffer[self.clock]

      self.anticip = []
      for i in range(self.clock+1, self.clock+11):
        if i in self.anticip_buffer:
          self.anticip += self.anticip_buffer[i]