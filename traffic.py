from sys import exit
from car import Car

"""
Represents different traffic strategies.
"""
class Traffic:
  def __init__(self, env, intersections, links):
    self.env = env
    self.intersections = intersections
    self.links = links
    self.strategies = {
      "basic": self.run_basic,
      "blind-shortest": self.run_blind_shortest
    }

  def get_traffic_strategy(self, name, param={}):
    if name not in self.strategies:
      print("Strategy", name, "does not exist")
      exit()

    return self.strategies[name](param)

  # Spawns a new car every new time step at a random intersection (for a maximum of `num` cars)
  # Cars when spawned follow the shortest path to their destination (Dijkstra)
  def run_blind_shortest(self, param):
    print("start blind-shortest traffic")
    num = param["num"] if param["num"] else 5
    
    for _ in range(num):
      yield self.env.timeout(1)
      self.env.process(Car.generate_blind_shortest_car(self.env, self.links, self.intersections))


  # Spawns a new car every new time step at a random intersection (for a maximum of `num` cars)
  # Cars when spawned go to random links until they reach their destination (or a dead-end)
  def run_basic(self, param):
    print("start basic traffic")
    num = param["num"] if param["num"] else 5

    for _ in range(num):
      yield self.env.timeout(1)
      self.env.process(Car.generate_basic_car(self.env, self.links, self.intersections))