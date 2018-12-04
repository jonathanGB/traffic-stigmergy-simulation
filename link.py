import numpy as np

"""
Represents a road link between two intersections.
Links are discretized into a matrix of cells. The number of rows is the number of lanes, and
the number of columns is the different places occupied by a car on a lane.
Every cell is represented as a Simpy resource with 1-capacity (so there's only one car per resource).
 env: Simpy environment
 out_intersections: Reference to the intersection at the end of the link
 cells: matrix of simpy.Resource
 edge: data about the edge (generated by the topology parser)...
  {
   "lanes": number of lanes,
   "l":     Euclidean length of the lane,
   "vmax":  maximum speed on the lane,
   "cells": number of cells in a lane,
   "cap":   capacity of the link (number of cells * number of lanes)
  }
 cache: stigmergy cache
 num_cars: number of cars on the link at the current time
"""
class Link:
  
  def __init__(self, env, cells, out_intersec_cells, edge, cache, monitor):
    self.cells = cells
    self.out_intersec_cells = out_intersec_cells
    self.cache = cache # holds stigmergy info for the lane
    self.monitor = monitor
    self.env = env
    self.data = edge
    self.out_intersection = None # Nil, until set by the setter (Intersections are created after Links)
    self.in_intersection = None # Nil, until set by the setter (Intersections are created after Links)
    self.num_cars = 0 # how many cars on the link currently

  def set_out_intersection(self, intersection):
    self.out_intersection = intersection

  def set_in_intersection(self, intersection):
    self.in_intersection = intersection

  def get_out_intersection(self):
    return self.out_intersection

  def get_in_intersection(self):
    return self.in_intersection

  def get_cache(self):
    return self.cache

  def get_cap(self):
    return self.data["cap"]

  def get_num_cars(self):
    return self.num_cars

  def register_to_monitor(self):
    self.monitor.register_link(self)

  # TODO: maybe more processing (update link stats?)
  def ping_monitor_car_moving(self, car_id, data):
    self.monitor.update_car_moving(car_id, data)

  # TODO: maybe more processing (update link stats?)
  def ping_monitor_car_stopped(self, car_id):
    self.monitor.update_car_stopped(car_id)

  def register_cells(self):
    for i in range(len(self.cells)):
      lane = self.cells[i]
      N = len(lane)
      self.out_intersec_cells[i].register_link(self, i, N)

      for j in range(N):
        self.cells[i][j].register_link(self, i, j)

  # Use this method to update the number of cars on the current link
  # "1" to increment, "-1" to decrement
  def update_num_cars(self, delta):
    self.num_cars += delta

  # At this point, the car has accessed the buffer to the intersection.
  # We estimate that the car is no longer on the link it used to be at this point.
  def access_intersection(self):
    self.update_num_cars(-1) # car has left the link
    return self.get_out_intersection()

  def get_intersection_cell(self, pos):
    lane = pos[0]
    return self.out_intersec_cells[lane]

  """
  To request entry to a link, this method checks if any 1st cell on any lane is free.
  If not, returns a random cell.
  As well, it returns the coordinates of the cell (lane #, cell index), so that we can move
  the car accordingly when requesting the next cell in a lane (`get_next_cell`).
  """
  def request_entry(self):
    self.update_num_cars(1) # 1 new car on the link
    entry_cells = self.cells[:,0]

    for i, entry_cell in enumerate(entry_cells):
      if entry_cell.count == 0:
        return entry_cell, (i, 0)

    i = np.random.randint(0, self.data["lanes"])
    return entry_cells[i], (i, 0)

  """
  Given a position, returns whether or not this cell is next to the end intersection of the current
  link visited.
  """
  def is_next_to_intersection(self, pos):
    return pos[1] == self.data["cells"] - 1

  """
  Returns the cell next to the one given. By next, we mean the next one when the car is moving forward.
  """
  def get_next_cell(self, pos):
    if self.is_next_to_intersection(pos):
      raise StopIteration("Can't get next cell: next is an intersection")

    nextPos = (pos[0], pos[1]+1)
    return self.cells[nextPos], nextPos

  """
  Updates the link cache (for stigmergy) with the given delay provided by a car which has
  finished traveling through the link.
  """
  def store_stigmergy_data(self, delay):
    self.cache.store_data(delay + self.get_weight())

  """
  Returns the weight of this link.
  Current implementation only uses the number of cells 
  (which is proportionate to the time to traverse the link).
  Eventually, we'll want to involve stigmergy information.
  """
  def get_weight(self):
    return self.data["cells"]

  def __str__(self):
    return "to {}".format(self.out_intersection)

  def __repr__(self):
    return self.__str__()
