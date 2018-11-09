from time import time

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
    self.link = None # reference to the link on which the car currently is

  def set_link(self, link):
    self.link = link

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
    print("Car", self.id, "is running the basic strategy from", self.origin, "to", self.destination)

    while True:
      yield self.env.timeout(1)

      # TODO: if at intersection
        # check if dead-end: break if so
        # check if destination: break if so
        # otherwise: request the list of outgoing links, and request an initial cell to one of the link, and consume the cell when available (aka move there)
      # if at a cell: move forward
      

      print("moving car", self.id, "(but not really)")
