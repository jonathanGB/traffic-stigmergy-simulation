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
      "blind-shortest": self.run_blind_shortest,
      "case1": self.run_case1,
      "case2": self.run_case2
    }

  def get_traffic_strategy(self, name, param={}):
    if name not in self.strategies:
      print("Strategy", name, "does not exist")
      exit()

    return self.strategies[name](param)

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

  def run_case2(self, param):
    print("start case2 (long/short-term stigmergy) traffic")
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    procs = []
  
    # All start the cars at the same time in this strategy.
    # This induces more delays. We should probably keep adding more cars to test the strategies.
    # To measure differences in case 1, the strategy should run more than 1440 iterations (because
    # long-term stigmergy is updated every day). Using RealTimeEnvironment is going to be very long,
    # we should use an environment (without real-time) so that iterations run as fast as possible.
    for _ in range(num):
      procs.append(self.env.process(Car.generate_case2_car(self.env, self.links, self.intersections, omega)))

    yield self.env.timeout(20)
    
    for _ in range(num):
      procs.append(self.env.process(Car.generate_case2_car(self.env, self.links, self.intersections, omega)))

    yield from self.__wait_for_all_procs_to_finish(procs)

  def run_case1(self, param):
    print("start case1 (only long-term stigmergy) traffic")
    num = param["num"] if param["num"] else 5
    procs = []
  
    # All start the cars at the same time in this strategy.
    # This induces more delays. We should probably keep adding more cars to test the strategies.
    # To measure differences in case 1, the strategy should run more than 1440 iterations (because
    # long-term stigmergy is updated every day). Using RealTimeEnvironment is going to be very long,
    # we should use an environment (without real-time) so that iterations run as fast as possible.
    for _ in range(num):
      procs.append(self.env.process(Car.generate_case1_car(self.env, self.links, self.intersections)))

    yield from self.__wait_for_all_procs_to_finish(procs)

  """
  Spawns a new car every new time step at a random intersection (for a maximum of `num` cars).
  Cars when spawned follow the shortest path to their destination (Dijkstra).
  """
  def run_blind_shortest(self, param):
    print("start blind-shortest traffic")
    num = param["num"] if param["num"] else 5
    procs = []
    
    for _ in range(num):
      yield self.env.timeout(1)
      procs.append(self.env.process(Car.generate_blind_shortest_car(self.env, self.links, self.intersections)))

    yield from self.__wait_for_all_procs_to_finish(procs)

  """
  Spawns a new car every new time step at a random intersection (for a maximum of `num` cars).
  Cars when spawned go to random links until they reach their destination (or a dead-end).
  """
  def run_basic(self, param):
    print("start basic traffic")
    num = param["num"] if param["num"] else 5
    procs = []

    for _ in range(num):
      yield self.env.timeout(1)
      procs.append(self.env.process(Car.generate_basic_car(self.env, self.links, self.intersections)))

    yield from self.__wait_for_all_procs_to_finish(procs)