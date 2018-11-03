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

  def __init__(self, env, origin, destination, links):
    self.env = env
    self.origin = origin
    self.destination = destination
    self.links = links
    self.id = generate_id()
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
