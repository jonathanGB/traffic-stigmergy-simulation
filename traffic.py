from sys import exit
from car import Car
from math import ceil
import numpy as np

"""
Represents different traffic strategies.
"""
class Traffic:
  def __init__(self, env, intersections, links, monitor):
    self.env = env
    self.intersections = intersections
    self.links = links
    self.monitor = monitor
    self.traffics = {
      "nyc_weekday": self.run_nyc_weekday,
      "nyc_weekend": self.run_nyc_weekend,
      "kanamori": self.run_kanamori
    }

  def get_traffic_strategy(self, name, param={}):
    if name not in self.traffics:
      print("Strategy", name, "does not exist")
      exit()

    return self.traffics[name](param)

  """
  Helper generator method that terminates once all the given processes are terminated as well.
  We use this so that the simulation terminates when all the cars finish.
  This is necessary, because the stigmergy caches' processes never end,
  so we must clue the environment when the simulation should really end.
  """
  def __wait_for_all_procs_to_finish(self, procs):
    while len(procs) > 0:
      active_procs = []
      for proc in procs:
        if not proc.processed:
          active_procs.append(proc)

      procs = active_procs
      yield self.env.timeout(1)

  def run_nyc_weekday(self, param):
    print("start nyc weekday traffic")
    procs = []
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    alpha = param["alpha"]
    beta = param["beta"]
    perc = param["perc"]
    strategy = param["strategy"]
    hourly_traffic = [0.46,	0.29, 0.19,	0.16, 0.16,	0.27, 0.58, 0.94, 1.00,	0.93,\
                0.85, 0.84,	0.84, 0.83,	0.86, 0.88,	0.86, 0.87,	0.87, 0.88,	0.82,\
                0.78, 0.76, 0.71] #Traffic as % of max, hourly from 12-1am to 11pm-12am

    for i in range(1440 * 5):
      day = i // 1440
      hour = (i // 60) % 24 #Hour on 24-hour clock
      n_cars = ceil(num * hourly_traffic[hour]) #number of cars per minute
      for _ in range(n_cars): #Loop to generate multiple cars
        procs.append(self.env.process(Car.generate_nyc_car(strategy, day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))

      yield self.env.timeout(1)

    yield from self.__wait_for_all_procs_to_finish(procs)

  def run_nyc_weekend(self, param):
    print("start nyc weekend traffic")
    procs = []
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    alpha = param["alpha"]
    beta = param["beta"]
    perc = param["perc"]
    strategy = param["strategy"]
    hourly_traffic = [0.67, 0.53, 0.43, 0.35, 0.28, 0.20, 0.25, 0.36, 0.52, \
                      0.65, 0.74, 0.80, 0.84, 0.84, 0.83, 0.80, 0.80, 0.81, 0.84, 0.80, \
                      0.73, 0.68, 0.65, 0.61]  # Traffic as % of max, hourly from 12-1am to 11pm-12am

    for i in range(1440 * 5):
      day = i // 1440
      hour = (i // 60) % 24  # Hour on 24-hour clock
      n_cars = ceil(num * hourly_traffic[hour])  # number of cars per minute
      for _ in range(n_cars):  # Loop to generate multiple cars
        procs.append(self.env.process(
          Car.generate_nyc_car(strategy, day, param["verbose"], self.monitor, self.env, self.links, self.intersections,
                               omega, alpha, beta, perc)))

      yield self.env.timeout(1)

    yield from self.__wait_for_all_procs_to_finish(procs)

  def run_kanamori(self, param):
    print("start kanamori traffic")
    procs = []
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    alpha = param["alpha"]
    beta = param["beta"]
    perc = param["perc"]
    strategy = param["strategy"]
    
    for i in range(100):
      day = i // 1440
      hour = (i // 60) % 24 #Hour on 24-hour clock
      minute = i % 1440

      if minute < 100:
        if np.random.uniform() < .25:
          procs.append(self.env.process(Car.generate_car("case0", "v0", "v24", day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))
        else:
          procs.append(self.env.process(Car.generate_car(strategy, "v0", "v24", day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))
        
        if np.random.uniform() < .25:
          procs.append(self.env.process(Car.generate_car("case0", "v2", "v22", day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))
        else:
          procs.append(self.env.process(Car.generate_car(strategy, "v2", "v22", day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))
        
        if np.random.uniform() < .25:
          procs.append(self.env.process(Car.generate_car("case0", "v4", "v20", day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))
        else:
          procs.append(self.env.process(Car.generate_car(strategy, "v4", "v20", day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))
    
      yield self.env.timeout(1)

    yield from self.__wait_for_all_procs_to_finish(procs)