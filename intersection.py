import numpy as np

"""
Represents an intersection and handles requests to get out of the intersection.
Holds the out links from the intersection.
"""
class Intersection:
  def __init__(self, env, name, links):
    self.env = env
    self.id = name
    self.out = links

  def get_links(self):
    return self.out

  def get_random_link(self):
    return np.random.choice(self.out)

  def get_id(self):
    return self.id

  def is_deadend(self):
    return len(self.out) == 0

  def __str__(self):
    return "Intersection {}".format(self.id)

  # Note: This is only defined to satisfy the `heapq` library in `network.py`
  def __lt__(self, other):
    return True