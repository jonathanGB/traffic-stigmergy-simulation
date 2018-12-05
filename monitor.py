from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
from json import dump

class CarStatus(Enum):
  CREATED = "created"
  MOVING = "moving"
  STOPPED = "stopped"
  FINISHED = "finished"

"""
This class runs a daemon that gathers all metrics sent from cars and resources.
It also runs a drawing process.
"""
class Monitor:

  def __init__(self, env):
    self.env = env
    self.intersections = set()
    self.cars = {}
    self.links = {}
    self.finished_cars = set()

  def get_cars(self):
    return self.cars

  def register_car(self, car, day=0):
    self.cars[car.get_id()] = {
      "day": day,
      "origin": car.get_origin(),
      "destination": car.get_destination(),
      "travel_time": 0,
      "delay_time": 0,
      "status": CarStatus.CREATED,
      "pos": None # nil when created
    }

  def register_link(self, link):
    self.links[link] = {
      "volume_history": []
    }

  def update_car_moving(self, car_id, data):
    travel_time_delta, delay_time_delta, pos = data
    car = self.cars[car_id]
    car['travel_time'] += travel_time_delta
    car['delay_time'] += delay_time_delta
    car['status'] = CarStatus.MOVING
    car['pos'] = pos

  def update_car_stopped(self, car_id):
    self.cars[car_id]['status'] = CarStatus.STOPPED

  def update_car_finished(self, car_id):
    self.cars[car_id]['status'] = CarStatus.FINISHED

  def get_car_colour(self, car_status):
    if car_status == CarStatus.MOVING:
      return 'c'

    if car_status == CarStatus.FINISHED:
      return 'xkcd:golden rod'

    return 'r'

  @staticmethod
  def get_perpendicular_vector(deltax, deltay, curr_norm, final_norm):
    return np.array([deltay, -deltax]) / curr_norm * final_norm

  def get_car_position(self, car):
    offset = 100 # arbitrary offset from the line
    link, pos = car
    n = link.get_weight()
    start_intersec, end_intersec = link.get_in_intersection(), link.get_out_intersection()
    start_x, start_y = start_intersec.get_pos()
    end_x, end_y = end_intersec.get_pos()
    deltay, deltax = end_y - start_y, end_x - start_x

    l = np.sqrt(deltax**2 + deltay**2)
    k = 8/10 * l / n # don't use the full length of the link (to reduce overlaps)

    dist_from_start = pos[1] * k + 1/10 * l
    prop = dist_from_start / l
    new_x, new_y = deltax * prop + start_x, deltay * prop + start_y

    perp_vec = Monitor.get_perpendicular_vector(deltax, deltay, l, (pos[0] + 1) * offset)

    return new_x + perp_vec[0], new_y + perp_vec[1]

  def register_intersection(self, intersection):
    self.intersections.add(intersection)

  def draw_topology(self, ctr, area):
    visited_nodes = set()

    plt.axis(area)
    plt.figure(figsize=(20,20))
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.gca().axes.get_xaxis().set_visible(False)
    
    for intersection in self.intersections:
      visited_nodes.add(intersection)
      x, y = intersection.get_pos()

      plt.scatter(x, y, marker="*", s=60, zorder=2, color="w")

      for out in intersection.get_links():
        if out not in visited_nodes:
          out_x, out_y = out.get_out_intersection().get_pos()
          plt.plot([x, out_x], [y, out_y], color="xkcd:bland", zorder=1)

    for car_id in self.cars:
      car = self.cars[car_id]
      car_status = car['status']

      if car_id in self.finished_cars or car_status == CarStatus.CREATED or not car['pos']:
        continue

      if car_status == CarStatus.FINISHED:
        self.finished_cars.add(car_id)

      car_colour = self.get_car_colour(car_status)
      car_x, car_y = self.get_car_position(car['pos'])

      plt.scatter(car_x, car_y, marker='o', color=car_colour, s=50)
      plt.annotate(car_id, (car_x, car_y))

    plt.savefig("output/{:05d}.png".format(ctr))
    plt.close()

  def get_topology_area(self):
    n = len(self.intersections)
    xs, ys = np.zeros(n), np.zeros(n)

    for i, intersection in enumerate(self.intersections):
      xs[i], ys[i] = intersection.get_pos()

    min_x = xs.min() - 100
    max_x = xs.max() + 100
    min_y = ys.min() - 100
    max_y = ys.max() + 100

    return min_x, max_x, min_y, max_y

  def draw_network(self):
    area = self.get_topology_area()

    ctr = 0  
    while True:
      self.draw_topology(ctr, area)
      ctr += 1

      yield self.env.timeout(1)

  def output_stats(self, file_name):
    output = {}

    for car_id in self.cars:
      car = self.cars[car_id]
      day = car['day']

      if day not in output:
        output[day] = {
          "cars": {
            "delay_times": [],
            "travel_times": [],
            "prop_delays": [],
          }
        }

      output[day]['cars']['delay_times'].append(car['delay_time'])
      output[day]['cars']['travel_times'].append(car['travel_time'])
      output[day]['cars']['prop_delays'].append(round(car['delay_time'] / car['travel_time'], 3))

    with open('stats/{}'.format(file_name), 'w') as f:
      dump(output, f)