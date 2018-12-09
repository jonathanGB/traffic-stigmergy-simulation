from time import time
import numpy as np
from intersection import Intersection
from util import generate_id
import network
from topology import dist


"""
Represents a car as a Simpy process.
 env: Simpy environment
 origin: origin node (Intersection)
 destination: destination node (Intersection)
 links: links of the road network (Set of Link)
"""
class Car:
  id_generator = generate_id()

  def __init__(self, env, origin, destination, links, monitor, verbose):
    self.env = env
    self.origin = origin
    self.destination = destination
    self.links = links
    self.id = next(self.id_generator)
    self.monitor = monitor
    self.verbose = verbose
    self.cell = None # reference to the cell's resource
    self.curr_infra = origin # reference to the link OR intersection on which the car currently is
    self.total_delay = 0 # incurred delay since the beginning

  def get_id(self):
    return self.id

  def get_origin(self):
    return self.origin

  def get_destination(self):
    return self.destination

  def get_total_delay(self):
    return self.total_delay

  def set_curr_infra(self, infra):
    self.curr_infra = infra

  def is_at_intersection(self):
    return type(self.curr_infra) == Intersection

  @staticmethod
  def generate_nyc_car(strategy, day, verbose, monitor, env, links, intersections, omega, alpha, beta, perc):
    av_v_st = 7 #Ratio of traffic on avenues vs. streets, based on ratios from NYC open data
    edge_wtg = 10 #ratio of cars originating on the edges of the grid vs. center
    #Create list with orgins weighted by more likely end points
    origin_intersections = list(intersections) + \
            ['v1_1','v2_1','v4_1','v6_1','v1_16','v3_16','v5_16','v7_16'] * edge_wtg * av_v_st \
            + ['v1_3','v1_5','v1_7','v1_9','v1_11','v1_13','v1_15'] * edge_wtg \
            + ['v7_2','v7_4','v7_6','v7_8','v7_10','v7_12','v7_14'] * edge_wtg
    dest_intersections_S = list(intersections) + ['v1_1','v3_1','v5_1','v7_1'] \
            * edge_wtg * av_v_st + ['v1_2','v1_4','v1_6','v1_8','v7_1','v7_3', \
            'v7_5','v7_7',]* edge_wtg
    dest_intersections_N = list(intersections) + ['v1_16','v2_16','v4_16','v6_16'] \
            * edge_wtg * av_v_st + ['v1_10','v1_12','v1_14','v1_16','v7_9','v7_11', \
            'v7_13','v7_15']* edge_wtg
    origin_name = np.random.choice(origin_intersections, 1)[0]
    is_south = int(origin_name[origin_name.find('_')+1:]) < 9 #determines if origin is in the southern half of grid
    
    destination_name = origin_name
    while destination_name == origin_name:
      if is_south: 
        destination_name = np.random.choice(dest_intersections_N, 1)[0] #more heavily weight northern intersections for southern origins
      else:
        destination_name = np.random.choice(dest_intersections_S, 1)[0] #more heavily weight southern intersections for northern origins
    
    origin, destination = intersections[origin_name], intersections[destination_name]
    car = Car(env, origin, destination, links, monitor, verbose)
    car.monitor.register_car(car, day)

    return car.run_strategy(strategy, intersections, omega, alpha, beta, perc)

  @staticmethod
  def generate_car(strategy, origin_name, destination_name, day, verbose, monitor, env, links, intersections, omega, alpha, beta, perc):
    origin, destination = intersections[origin_name], intersections[destination_name]
    car = Car(env, origin, destination, links, monitor, verbose)
    car.monitor.register_car(car, day)

    return car.run_strategy(strategy, intersections, omega, alpha, beta, perc)

  def run_strategy(self, strat, intersections, omega, alpha, beta, perc):
    if strat == "case0":
      links_to_visit = network.shortest_path(self.origin, self.destination, self.links, intersections)
      return self.run_blind_shortest(links_to_visit)

    if strat == "case1":
      links_to_visit = network.shortest_path(self.origin, self.destination, self.links, intersections, network.case1_weight_query)
      return self.run_blind_shortest(links_to_visit)

    if strat == "case2":
      update_path = Car.__update_path_case2(self.destination, self.links, intersections, omega)
      links_to_visit = update_path(self.origin, False)
      return self.run_dynamic(links_to_visit, update_path, Car.__allocate_anticip_never())

    update_path = Car.__update_path_allocated_case(self.destination, self.links, intersections, omega, alpha, beta)
    links_to_visit = update_path(self.origin, False)

    if strat == "case3":
      return self.run_dynamic(links_to_visit, update_path, Car.__allocate_anticip_random())
    if strat == "case4":
      return self.run_dynamic(links_to_visit, update_path, Car.__allocate_anticip_by_distance(perc, self.verbose))
    if strat == "case5":
      return self.run_dynamic(links_to_visit, update_path, Car.__allocate_anticip_by_delay(perc, self.verbose))

    raise ValueError("Strategy {} does not exist".format(strat))

  """
  Allocation rules
  """
  @staticmethod
  def __allocate_anticip_never():
    def allocate_anticip(car, link):
      return False

    return allocate_anticip

  @staticmethod
  def __allocate_anticip_always():
    def allocate_anticip(car, link):
      return True

    return allocate_anticip

  @staticmethod
  def __allocate_anticip_random():
    def allocate_anticip(car, link):
      if not link.has_stigmergy:
        return True
        
      return np.random.uniform() < 0.5

    return allocate_anticip

  @staticmethod
  def __allocate_anticip_by_distance(perc, verbose):
    def allocate_anticip(car, link):
      if not link.has_stigmergy:
        return True

      own_distance = dist(car.curr_infra.get_pos(), car.destination.get_pos())
      shorter = 0
      longer = 0

      other_cars = link.get_cache().get_anticip_buffer()
      for id in other_cars:
        buf = other_cars[id]
        for other in buf:
          other_distance = dist(car.curr_infra.get_pos(), other.destination.get_pos())
          if own_distance > other_distance:
            shorter += 1
          else:
            longer += 1

      anticip = shorter > perc * (longer + shorter + 1)

      if verbose:
        print(car, "to", car.curr_infra, ": shorter =", shorter, ", longer =", longer, ", anticip =", anticip)

      return anticip

    return allocate_anticip

  @staticmethod
  def __allocate_anticip_by_delay(perc, verbose):
    def allocate_anticip(car, link):
      if not link.has_stigmergy:
        return True

      own_delay = car.get_total_delay()
      less_delay = 0
      more_delay = 0

      other_cars = link.get_cache().get_anticip_buffer()
      for id in other_cars:
        buf = other_cars[id]
        for other in buf:
          if own_delay > other.get_total_delay():
            less_delay += 1
          else:
            more_delay += 1

      anticip = less_delay > perc * (more_delay + less_delay + 1)
      if verbose:
        print(car, "to", car.curr_infra, ": less_delay =", less_delay, ", more_delay =", more_delay, ", anticip =", anticip)

      return anticip

    return allocate_anticip

  @staticmethod
  def __update_path_case2(destination, links, intersections, omega):
    def update_path(origin, _):
      return network.shortest_path(origin, destination, links, intersections, network.case2_weight_query(origin, omega))

    return update_path

  @staticmethod
  def __update_path_allocated_case(destination, links, intersections, omega, alpha, beta):
    def update_path(origin, allocated):
      if allocated:
        return network.shortest_path(origin, destination, links, intersections,
                                     network.anticipatory_weight_query(origin, alpha, beta))

      return network.shortest_path(origin, destination, links, intersections,
                                              network.case2_weight_query(origin, omega))

    return update_path

  def __update_link_intentions(self, links):
    cap_time = 10
    future_time = 0

    # We go in reversed order because the links are visited in reversed order.
    for link in reversed(links):
      time_to_traverse_link = link.get_weight()
      future_time += time_to_traverse_link

      # update time when the car should be on the link.
      # cap_time is 10, because we only look 10 minutes in the future.
      # if future_time >= cap_time, we update the stigmergy for 10 minutes in the future, and stop.
      if future_time < cap_time:
        link.get_cache().increment_anticip_stigmergy(self, future_time)
      else:
        link.get_cache().increment_anticip_stigmergy(self, cap_time)
        break

  def run_dynamic(self, path, update_path, allocate_anticip):
    if self.verbose:
      print(self, "is running the dynamic strategy from", self.origin, "to", self.destination)
      print("Its path will be (in reversed order):", path, "\n")
    intersec_cell = None
    t = 0

    # update intentions in next 10 mins (stigmergy caches)
    self.__update_link_intentions(path)

    while len(path) > 0:
      ongoing_link = path.pop()
      cell, pos = ongoing_link.request_entry()
      cell_req = cell.request(self.get_id())
      link_delay = 0

      delay = yield from cell_req # wait to have access to the cell
      if intersec_cell:
        intersec_cell.release(self.id)

      t += delay
      link_delay += delay
      if self.verbose:
        print(self, "has accessed the link toward", ongoing_link.get_out_intersection(), "(delay:", link_delay, ") [", self.destination, "]")

      # keep moving on the link
      while True:
        # now we have access to the cell
        yield self.env.timeout(1)
        t += 1
        # TODO:  update monitor with travel movement

        # update path every 5 minutes
        if t >= 5:
          t = 0
          allocated = allocate_anticip(self, ongoing_link)

          path = update_path(ongoing_link.get_out_intersection(), allocated)

          # update intentions in next 10 mins (stigmergy caches)
          self.__update_link_intentions(path)

        # we have reached the end of the link, we need to update stigmergy information about the visited link.
        # Notice, that we first need to request access to the intersection before.
        # Initially, we didn't put a capacity for intersections, and so technically it could have been possible
        # to have an infinity of cars at an intersection. This was especially bad when updating stigmergy caches,
        # because the time spent in the intersection was not accounted. Now, we have a special cell (resource), one
        # per outgoing lane to that intersection.
        if ongoing_link.is_next_to_intersection(pos):
          intersec_cell = ongoing_link.get_intersection_cell(pos)
          intersec_cell_req = intersec_cell.request(self.get_id())
          delay = yield from intersec_cell_req
          t += delay
          link_delay += delay

          cell.release(self.get_id())
          ongoing_link.store_stigmergy_data(link_delay)
          break

        next_cell, next_pos = ongoing_link.get_next_cell(pos)
        next_cell_req = next_cell.request(self.get_id())
        delay = yield from next_cell_req
        t += delay
        link_delay += delay

        cell.release(self.get_id())
        cell, pos, cell_req = next_cell, next_pos, next_cell_req

      # car is now at a new intersection
      self.total_delay += link_delay # should be useful for case 5
      self.curr_infra = ongoing_link.access_intersection()
      if self.verbose:
        print(self, "is at intersection", self.curr_infra)
    
    if intersec_cell:
      intersec_cell.release(self.id)

    self.monitor.update_car_finished(self.id)

  """
  Run the car process through the shortest path.
  The shortest path in this process is blind to stigmergy.
  Right now, the logic of this run is very similar to `run_basic`, except the links are popped
  from the path list computed via Dijkstra (rather than a random walk).
  """
  def run_blind_shortest(self, path):
    if self.verbose:
      print(self, "is running the blind-shortest strategy from", self.origin, "to", self.destination)
      print("Its path will be (in reversed order):", path, "\n")
    
    intersec_cell = None

    while len(path) > 0:
      ongoing_link = path.pop()
      cell, pos = ongoing_link.request_entry()
      cell_req = cell.request(self.get_id())
      link_delay = 0

      link_delay += yield from cell_req # wait to have access to the cell
      if intersec_cell:
        intersec_cell.release(self.id)
      if self.verbose:
        print(self, "has accessed the link toward", ongoing_link.get_out_intersection(), "(delay:", link_delay, ") [", self.destination, "]")

      # keep moving on the link
      while True:
        # now we have access to the cell
        yield self.env.timeout(1)

        # we have reached the end of the link, we need to update stigmergy information about the visited link.
        # Notice, that we first need to request access to the intersection before.
        # Initially, we didn't put a capacity for intersections, and so technically it could have been possible
        # to have an infinity of cars at an intersection. This was especially bad when updating stigmergy caches,
        # because the time spent in the intersection was not accounted. Now, we have a special cell (resource), one
        # per outgoing lane to that intersection.
        if ongoing_link.is_next_to_intersection(pos):
          intersec_cell = ongoing_link.get_intersection_cell(pos)
          intersec_cell_req = intersec_cell.request(self.get_id())
          link_delay += yield from intersec_cell_req

          cell.release(self.get_id())
          ongoing_link.store_stigmergy_data(link_delay)
          break

        next_cell, next_pos = ongoing_link.get_next_cell(pos)
        next_cell_req = next_cell.request(self.get_id())
        link_delay += yield from next_cell_req

        cell.release(self.get_id())
        cell, pos, cell_req = next_cell, next_pos, next_cell_req

      # car is now at a new intersection
      self.curr_infra = ongoing_link.access_intersection()
      if self.verbose:
        print(self, "is at intersection", self.curr_infra)

    if intersec_cell:
      intersec_cell.release(self.id)

    self.monitor.update_car_finished(self.id)

  def __str__(self):
    return "Car {}".format(self.id)