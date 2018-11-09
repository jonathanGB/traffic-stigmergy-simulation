from sys import exit
from car import Car
import numpy as np

"""
Represents different traffic strategies.
"""
class Traffic:
  def __init__(self, env, intersections, links):
    self.env = env
    self.intersections = intersections
    self.links = links
    self.strategies = {
      "basic": self.run_basic
    }

  def get_traffic_strategy(self, name):
    if name not in self.strategies:
      print("Strategy", name, "does not exist")
      exit()

    return self.strategies[name]()

  # Spawns a new car every new time step at a random intersection
  # Cars when spawned go to random links until they reach their destination (or a dead-end)
  def run_basic(self):
    print("start basic traffic")
    intersections_list = list(self.intersections)

    while True:
      yield self.env.timeout(1)
      self.env.process(self.__generate_basic_car(intersections_list))

  def __generate_basic_car(self, intersections_list):
    origin, destination = np.random.choice(intersections_list, 2, replace=False)
    return Car(self.env, origin, destination, self.links).run_basic()