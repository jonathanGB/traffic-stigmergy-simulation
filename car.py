from time import time
import numpy as np
from intersection import Intersection
from util import generate_id
import network


"""
Represents a car as a Simpy process.
 env: Simpy environment
 origin: origin node (Intersection)
 destination: destination node (Intersection)
 links: links of the road network (Set of Link)
"""
class Car:
  id_generator = generate_id()

  def __init__(self, env, origin, destination, links):
    self.env = env
    self.origin = origin
    self.destination = destination
    self.links = links
    self.id = next(self.id_generator)
    self.cell = None # reference to the cell's resource
    self.curr_infra = origin # reference to the link OR intersection on which the car currently is

  def set_curr_infra(self, infra):
    self.curr_infra = infra

  def is_at_intersection(self):
    return type(self.curr_infra) == Intersection

  """
  Factory of "basic" cars.
  """
  @staticmethod
  def generate_basic_car(env, links, intersections):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    return Car(env, intersections[origin_name], intersections[destination_name], links).run_basic()

  """
  Factory of cars following the shortest path (case 0: not information)
  """
  @staticmethod
  def generate_blind_shortest_car(env, links, intersections):
    origin_name, destination_name = np.random.choice(list(intersections), 2, replace=False)
    origin, destination = intersections[origin_name], intersections[destination_name]
    links_to_visit = network.shortest_path(origin, destination, links, intersections)
    return Car(env, origin, destination, links).run_blind_shortest(links_to_visit)

  # def run(self):
  #   trajectory = self.get_shortest_path()

  #   analytics = {
  #     "raw-time": time(),
  #     "time-steps": 0
  #   }
  #   # while True:
  #     # TODO: move the car by consuming the cell resource until destination reached
  #     # TODO: update the car analytics 
  #     # TODO: update graph with stigmergy data

  """
  Run the car process through the shortest path.
  The shortest path in this process is blind to stigmergy.
  Right now, the logic of this run is very similar to `run_basic`, except the links are popped
  from the path list computed via Dijkstra (rather than a random walk).
  """
  def run_blind_shortest(self, path):
    print(self, "is running the blind-shortest strategy from", self.origin, "to", self.destination)
    print("Its path will be (in reversed order):", path, "\n")

    while len(path) > 0:
      ongoing_link = path.pop()
      cell, pos = ongoing_link.request_entry()
      cell_req, cell_req_token = cell.request()
      link_delay = 0

      link_delay += yield from cell_req # wait to have access to the cell
      print(self, "has accessed the link toward", ongoing_link.get_out_intersection(), "(delay:", link_delay, ") [", self.destination, "]")
      
      # keep moving on the link
      while True:
        # now we have access to the cell
        yield self.env.timeout(1)

        # we have reached the end of the link, we need to update stigmergy information about the visited link
        if ongoing_link.is_next_to_intersection(pos):
          cell.release(cell_req_token)
          ongoing_link.store_stigmergy_data(link_delay)
          break

        next_cell, next_pos = ongoing_link.get_next_cell(pos)
        next_cell_req, next_cell_req_token = next_cell.request()
        link_delay += yield from next_cell_req

        cell.release(cell_req_token)
        cell, pos, cell_req, cell_req_token = next_cell, next_pos, next_cell_req, next_cell_req_token

      # car is now at a new intersection
      self.curr_infra = ongoing_link.access_intersection()
      print(self, "is at intersection", self.curr_infra)
      yield self.env.timeout(1)


  """
  Run the basic Car process (where cars pretty much go randomly until they reach their destination)
  """
  def run_basic(self):
    print(self, "is running the basic strategy from", self.origin, "to", self.destination)

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
      cell_req, cell_req_token = cell.request()
      yield from cell_req # wait to have access to the cell
      print(self, "has accessed the link toward intersection", ongoing_link.get_out_intersection(), "(", self.destination, ")")

      # keep moving on the link
      while True:
        # now we have access to the cell
        print(self, "moved to cell", pos)
        yield self.env.timeout(1)

        if ongoing_link.is_next_to_intersection(pos):
          cell.release(cell_req_token)
          break

        next_cell, next_pos = ongoing_link.get_next_cell(pos)
        next_cell_req, next_cell_req_token = next_cell.request()
        yield from next_cell_req

        cell.release(cell_req_token)
        cell, pos, cell_req, cell_req_token = next_cell, next_pos, next_cell_req, next_cell_req_token

      # car is now at a new intersection
      self.curr_infra = ongoing_link.access_intersection()
      print(self, "is at intersection", self.curr_infra)
      yield self.env.timeout(1)

  def __str__(self):
    return "Car {}".format(self.id)