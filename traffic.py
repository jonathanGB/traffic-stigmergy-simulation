from sys import exit
from car import Car
from math import ceil

"""
Represents different traffic strategies.
"""
class Traffic:
  def __init__(self, env, intersections, links, monitor):
    self.env = env
    self.intersections = intersections
    self.links = links
    self.monitor = monitor
    self.strategies = {
      "basic": self.run_basic,
      "blind-shortest": self.run_blind_shortest,
      "case1": self.run_case1,
      "case2": self.run_case2,
      "case3": self.run_case3,
      "case4": self.run_case4,
      "case5": self.run_case5,
      "nyc_weekday_basic": self.run_nyc_weekday_basic,
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

  def run_case5(self, param):
    print("start case5 (anticipatory stigmergy with allocation strategy) traffic")
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    alpha = param["alpha"]
    beta = param["beta"]
    perc = param["perc"]
    procs = []

    # All start the cars at the same time in this strategy.
    # This induces more delays. We should probably keep adding more cars to test the strategies.
    # To measure differences in case 1, the strategy should run more than 1440 iterations (because
    # long-term stigmergy is updated every day). Using RealTimeEnvironment is going to be very long,
    # we should use an environment (without real-time) so that iterations run as fast as possible.
    for _ in range(num):
      procs.append(self.env.process(Car.generate_case5_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))

    yield self.env.timeout(20)

    for _ in range(num):
      procs.append(self.env.process(Car.generate_case5_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))

    yield from self.__wait_for_all_procs_to_finish(procs)

  def run_case4(self, param):
    print("start case4 (anticipatory stigmergy with allocation strategy by distance) traffic")
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    alpha = param["alpha"]
    beta = param["beta"]
    perc = param["perc"]
    procs = []

    # All start the cars at the same time in this strategy.
    # This induces more delays. We should probably keep adding more cars to test the strategies.
    # To measure differences in case 1, the strategy should run more than 1440 iterations (because
    # long-term stigmergy is updated every day). Using RealTimeEnvironment is going to be very long,
    # we should use an environment (without real-time) so that iterations run as fast as possible.
    for _ in range(num):
      procs.append(self.env.process(Car.generate_case4_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))

    yield self.env.timeout(20)

    for _ in range(num):
      procs.append(self.env.process(Car.generate_case4_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))

    yield from self.__wait_for_all_procs_to_finish(procs)

  def run_case3(self, param):
    print("start case3 (anticipatory stigmergy without allocation strategy by delay) traffic")
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    alpha = param["alpha"]
    beta = param["beta"]
    procs = []

    # All start the cars at the same time in this strategy.
    # This induces more delays. We should probably keep adding more cars to test the strategies.
    # To measure differences in case 1, the strategy should run more than 1440 iterations (because
    # long-term stigmergy is updated every day). Using RealTimeEnvironment is going to be very long,
    # we should use an environment (without real-time) so that iterations run as fast as possible.
    for _ in range(num):
      procs.append(self.env.process(Car.generate_case3_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta)))

    yield self.env.timeout(20)

    for _ in range(num):
      procs.append(self.env.process(Car.generate_case3_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta)))

    yield from self.__wait_for_all_procs_to_finish(procs)

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
      procs.append(self.env.process(Car.generate_case2_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega)))

    yield self.env.timeout(20)

    for _ in range(num):
      procs.append(self.env.process(Car.generate_case2_car(param["verbose"], self.monitor, self.env, self.links, self.intersections, omega)))

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
      procs.append(self.env.process(Car.generate_case1_car(param["verbose"], self.monitor, self.env, self.links, self.intersections)))

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
      procs.append(self.env.process(Car.generate_blind_shortest_car(param["verbose"], self.monitor, self.env, self.links, self.intersections)))

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
      procs.append(self.env.process(Car.generate_basic_car(param["verbose"], self.monitor, self.env, self.links, self.intersections)))

    yield from self.__wait_for_all_procs_to_finish(procs)

  def run_nyc_weekday_basic(self, param):
    """
    Runs basic traffic strategy (Dijkstra shortest path) on NYC grid with week day
    traffic patterns
    """
    print("start nyc weekday basic traffic")
    procs = []
    num = param["num"] if param["num"] else 5
    omega = param["omega"]
    alpha = param["alpha"]
    beta = param["beta"]
    perc = param["perc"]
    hourly_traffic = [0.46,	0.29, 0.19,	0.16, 0.16,	0.27, 0.58, 0.94, 1.00,	0.93,\
                0.85, 0.84,	0.84, 0.83,	0.86, 0.88,	0.86, 0.87,	0.87, 0.88,	0.82,\
                0.78, 0.76, 0.71] #Traffic as % of max, hourly from 12-1am to 11pm-12am

    for i in range(1440 * 5):
      day = i // 1440
      hour = (i // 60) % 24 #Hour on 24-hour clock
      n_cars = ceil(num * hourly_traffic[hour]) #number of cars per minute
      for _ in range(n_cars): #Loop to generate multiple cars
        procs.append(self.env.process(Car.generate_nyc_car(day, param["verbose"], self.monitor, self.env, self.links, self.intersections, omega, alpha, beta, perc)))

      yield self.env.timeout(1)


    yield from self.__wait_for_all_procs_to_finish(procs)

  """
  Spawns a new car every new time step at a random intersection (for a maximum of `num` cars).
  Cars when spawned go to random links until they reach their destination (or a dead-end).
  """
  # def run_nyc_weekend(self, param):
  #   print("start nyc weekend traffic")
  #   time = 0 #hour of day on 24 hour clock
  #   hourly_traffic = [0.67, 0.53, 0.43, 0.35, 0.28, 0.20, 0.25, 0.36, 0.52,\
  #           0.65, 0.74, 0.80, 0.84, 0.84, 0.83, 0.80, 0.80, 0.81, 0.84, 0.80,\
  #           0.73, 0.68, 0.65, 0.61] #Traffic as % of max, hourly from 12-1am to 11pm-12am
  #   num = param["num"] if param["num"] else 10 * int(hourly[time]) #~300 cars per minute would be rush-hour traffic
  #   procs = []
  #   for _ in range(num):
  #     yield self.env.timeout(1)
  #     procs.append(self.env.process(Car.generate_basic_car(self.env, self.links, self.intersections)))

  #   yield from self.__wait_for_all_procs_to_finish(procs)
