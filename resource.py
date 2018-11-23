from collections import deque
from util import generate_id


"""
We could use `Simpy.Resource`s, but they do not provide the ability to compute the delay of requesting cells.
This metric is crucial for stigmergy, so we implemented a representation of a resource which returns the delay
once the request of the resource is completed.
"""
class Resource:
  def __init__(self, env):
    self.env = env
    self.q = deque()
    self.tokenator = generate_id()

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
  def request(self):
    token = next(self.tokenator) # generate token to identify the request in the queue
    return self.__request(token), token

  def __request(self, token):
    self.q.append(token)
    delay = 0

    while True:
      if self.q[0] == token:
        break

      yield self.env.timeout(1)
      delay += 1

    return delay

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
