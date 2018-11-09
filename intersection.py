
"""
Represents an intersection and handles requests to access the to and out of the intersection.
"""
class Intersection:
  def __init__(self, env, links):
    self.env = env
    self.links = links
    self.deadend = True