from time import time
import numpy as np
from intersection import Intersection


"""
Returns a new generated ID (generator function).
This might be useful to differenciate cars.
"""
def generate_id():
  id = 0
  while True:
    yield id
    id += 1


"""
Represents a car as a Simpy process.
 env: Simpy environment
 origin: origin node
 destination: destination node
 links: links of the road network
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

  @staticmethod
  def generate_basic_car(env, links, intersections):
    origin, destination = np.random.choice(list(intersections), 2, replace=False)
    return Car(env, intersections[origin], intersections[destination], links).run_basic()

  """
  Returns a list of links to visit in order to get from the origin to the destination.
  !! Not implemented yet !!
  """
  def get_shortest_path(self):
    # TODO: implement Dijkstra's shortest path
    return []

  """
  Run the Car process.
  """
  def run(self):
    trajectory = self.get_shortest_path()

    analytics = {
      "raw-time": time(),
      "time-steps": 0
    }
    # while True:
      # TODO: move the car by consuming the cell resource until destination reached
      # TODO: update the car analytics 
      # TODO: update graph with stigmergy data

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
      cell_req = cell.request()
      yield cell_req # wait to have access to the cell
      print(self, "has accessed the link toward intersection", ongoing_link.get_out_intersection(), "(", self.destination, ")")

      # keep moving on the link
      while True:
        # now we have access to the cell
        print(self, "moved to cell", pos)
        yield self.env.timeout(1)

        if ongoing_link.is_next_to_intersection(pos):
          cell.release(cell_req)
          break

        next_cell, next_pos = ongoing_link.get_next_cell(pos)
        next_cell_req = next_cell.request()
        yield next_cell_req

        cell.release(cell_req)
        cell, pos, cell_req = next_cell, next_pos, next_cell_req

      # car is now at a new intersection
      self.curr_infra = ongoing_link.access_intersection()
      print(self, "is at intersection", self.curr_infra)
      yield self.env.timeout(1)

  def __str__(self):
    return "Car {}".format(self.id)