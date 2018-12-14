from collections import deque
from monitor import CarStatus

"""
We could use `Simpy.Resource`s, but they do not provide the ability to compute the delay of requesting cells.
This metric is crucial for stigmergy, so we implemented a representation of a resource which returns the delay
once the request of the resource is completed.
"""
class Resource:
  def __init__(self, env):
    self.env = env
    self.link = None # sets once the link is instanciated
    self.pos = None # sets once the link is instanciated
    self.q = deque()

  """
  Register the underlying link of the resource. Links is only instanciated after the resources have been created, so
  we have to register separately.
  This reference makes it possible for the resources to publish to the monitor (link handles this task).
  """
  def register_link(self, link, i, j):
    self.link = link
    self.pos = (link, (i, j))

  """
  Returns the number of cars queued for the resource
  """
  @property
  def count(self):
    return len(self.q)

  """
  Initiate requesting access to the resource.
  Returns a generator to call afterwards in order to truly request the resource, as well as the token
  to identify the request (necessary when releasing). 
  """
  def request(self, car_id):
    return self.__request(car_id)

  def __request(self, token):
    self.q.append(token)
    delay = 0

    while True:
      if self.q[0] == token:
        self.link.ping_monitor_car_moving(token, (1, delay, self.pos))
        return delay

      if delay == 0:
        self.link.ping_monitor_car_stopped(token)
        
      yield self.env.timeout(1)
      delay += 1

  """
  Once we do not need the resource anymore, we need to release it for other cars to be able to access it.
  Requires the token given by `request` to authenticate the release.
  """
  def release(self, token):
    if len(self.q) == 0:
      raise IndexError("Can't release from an empty queue!")
    if self.q[0] != token:
      raise IndexError("Can't release if the car is not the first in the queue!")

    self.q.popleft()
