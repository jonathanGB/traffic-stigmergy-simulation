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

  def __init__(self, env, origin, destination, links, monitor):
    self.env = env
    self.origin = origin
    self.destination = destination
    self.links = links
    self.id = next(self.id_generator)
    self.monitor = monitor
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

  """
  Factory of "basic" cars.
  """
  @staticmethod
  def generate_basic_car(monitor, env, links, intersections):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    return Car(env, intersections[origin_name], intersections[destination_name], links, monitor).run_basic()

  """
  Factory of cars following the shortest path (case 0: not information)
  """
  @staticmethod
  def generate_blind_shortest_car(monitor, env, links, intersections):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    origin, destination = intersections[origin_name], intersections[destination_name]
    links_to_visit = network.shortest_path(origin, destination, links, intersections)
    return Car(env, origin, destination, links, monitor).run_blind_shortest(links_to_visit)

  """
  Factory of cars following case 1 (only long-term stigmergy).
  Case 1 cars also use `run_blind_shortest`, the difference from case 0 (blind-shortest) is that
  the path computed at first uses long-term stigmergy rather than simply the default weight of each links.
  That change can be seen in the extra parameter of `network.shortest_path`.
  """
  @staticmethod
  def generate_case1_car(monitor, env, links, intersections):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    origin, destination = intersections[origin_name], intersections[destination_name]
    links_to_visit = network.shortest_path(origin, destination, links, intersections, network.case1_weight_query)
    return Car(env, origin, destination, links, monitor).run_blind_shortest(links_to_visit)

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
      return np.random.uniform() < 0.5

    return allocate_anticip

  @staticmethod
  def __allocate_anticip_by_distance(perc):
    def allocate_anticip(car, link):
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
      print(car, "to", car.curr_infra, ": shorter =", shorter, ", longer =", longer, ", anticip =", anticip)

      return anticip

    return allocate_anticip

  @staticmethod
  def __allocate_anticip_by_delay(perc):
    def allocate_anticip(car, link):
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
      print(car, "to", car.curr_infra, ": less_delay =", less_delay, ", more_delay =", more_delay, ", anticip =", anticip)

      return anticip

    return allocate_anticip

  """
  Factory of cars following case 2 (long/short-term stigmergy).
  Here, we use `run_dynamic` rather than `run_blind_shortest`. This is because every 5 iterations,
  the path of the cars is updated based on stigmergy data.
  Notice that `run_dynamic` takes a function as a 2nd parameter which defines how to update the path.
  We use this functional abstraction so that we can still use `run_dynamic` in case3 and beyond,
  simply by changing that update function.
  """
  @staticmethod
  def generate_case2_car(monitor, env, links, intersections, omega):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    origin, destination = intersections[origin_name], intersections[destination_name]
    links_to_visit =  Car.__update_path_case2(destination, links, intersections, omega)(origin, False)

    return Car(env, origin, destination, links, monitor).run_dynamic(links_to_visit,
                                                            Car.__update_path_case2(destination, links, intersections, omega),
                                                            Car.__allocate_anticip_never())

  @staticmethod
  def __update_path_case2(destination, links, intersections, omega):
    def update_path(origin, _):
      return network.shortest_path(origin, destination, links, intersections, network.case2_weight_query(origin, omega))

    return update_path

  @staticmethod
  def generate_case3_car(monitor, env, links, intersections, omega, alpha, beta):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    origin, destination = intersections[origin_name], intersections[destination_name]

    update_path = Car.__update_path_allocated_case(destination, links, intersections, omega, alpha, beta)
    links_to_visit = update_path(origin, False)

    return Car(env, origin, destination, links, monitor).run_dynamic(links_to_visit, update_path, Car.__allocate_anticip_random())

  @staticmethod
  def generate_case4_car(monitor, env, links, intersections, omega, alpha, beta, perc):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    origin, destination = intersections[origin_name], intersections[destination_name]

    update_path = Car.__update_path_allocated_case(destination, links, intersections, omega, alpha, beta)
    links_to_visit = update_path(origin, False)

    return Car(env, origin, destination, links, monitor).run_dynamic(links_to_visit, update_path, Car.__allocate_anticip_by_distance(perc))

  @staticmethod
  def generate_case5_car(monitor, env, links, intersections, omega, alpha, beta, perc):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    origin, destination = intersections[origin_name], intersections[destination_name]

    update_path = Car.__update_path_allocated_case(destination, links, intersections, omega, alpha, beta)
    links_to_visit = update_path(origin, False)

    return Car(env, origin, destination, links, monitor).run_dynamic(links_to_visit, update_path, Car.__allocate_anticip_by_delay(perc))

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
    self.monitor.register_car(self)
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
    self.monitor.register_car(self)
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
      print(self, "is at intersection", self.curr_infra)

    if intersec_cell:
      intersec_cell.release(self.id)

    self.monitor.update_car_finished(self.id)


  """
  Run the basic Car process (where cars pretty much go randomly until they reach their destination)
  """
  def run_basic(self):
    self.monitor.register_car(self)
    print(self, "is running the basic strategy from", self.origin, "to", self.destination)
    intersec_cell = None


    while True:
      # check if dead-end: break if so
      if self.curr_infra.is_deadend():
        print(self, "arrived at a deadend!\n")
        break

      # check if destination: break if so
      if self.curr_infra == self.destination:
        print(self, "has arrived at its destination!\n")
        break

      # otherwise: request entry to a random outgoing link
      ongoing_link = self.curr_infra.get_random_link()
      cell, pos = ongoing_link.request_entry()
      cell_req = cell.request(self.get_id())
      yield from cell_req # wait to have access to the cell
      if intersec_cell:
        intersec_cell.release(self.id)
      print(self, "has accessed the link toward intersection", ongoing_link.get_out_intersection(), "(", self.destination, ")")

      # keep moving on the link
      while True:
        # now we have access to the cell
        print(self, "moved to cell", pos)
        yield self.env.timeout(1)

        if ongoing_link.is_next_to_intersection(pos):
          intersec_cell = ongoing_link.get_intersection_cell(pos)
          intersec_cell_req = intersec_cell.request(self.get_id())
          yield from intersec_cell_req

          cell.release(self.get_id())
          break

        next_cell, next_pos = ongoing_link.get_next_cell(pos)
        next_cell_req = next_cell.request(self.get_id())
        yield from next_cell_req

        cell.release(self.get_id())
        cell, pos, cell_req = next_cell, next_pos, next_cell_req

      # car is now at a new intersection
      self.curr_infra = ongoing_link.access_intersection()
      print(self, "is at intersection", self.curr_infra)
      yield self.env.timeout(1)

    if intersec_cell:
      intersec_cell.release(self.id)
    
    self.monitor.update_car_finished(self.id)


  def __str__(self):
    return "Car {}".format(self.id)
