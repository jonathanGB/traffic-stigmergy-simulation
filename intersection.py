import numpy as np

"""
Represents an intersection and handles requests to get out of the intersection.
Holds the out links from the intersection.
Visible links are set of  links that are visible for short-term stigmergy from that intersection.
"""
class Intersection:
  def __init__(self, env, name, links, visible_links):
    self.env = env
    self.id = name
    self.out = links
    self.visible_links = visible_links

  def get_links(self):
    return self.out

  def get_links_in_area(self):
    return self.visible_links

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