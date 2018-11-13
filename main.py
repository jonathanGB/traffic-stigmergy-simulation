import topology as topo
import simpy as sim
import numpy as np
from link import Link
from cache import Cache
from traffic import Traffic
from intersection import Intersection
import commandline

"""
Returns a mxn matrix containing 1-capacity resources.
This matrix represents the cells where cars can be.
The resources have 1-capacity, so that only one car is present in one cell
 env: simpy environment
 m: number of lanes
 n: number of cells in one lane
"""
def initialize_road_cells(env, m, n):
  return np.array([[sim.Resource(env, 1) for j in range(n)] for i in range(m)])

args = commandline.parse()

N, E = topo.topology_parser(args["network"])

env = sim.RealtimeEnvironment()
links = {} # holds references to the links of the road network
intersections = {} # holds references to the intersections of the road network
for trajectory in E:
  edge = E[trajectory]
  cells = initialize_road_cells(env, edge['lanes'], edge['cells'])

  links[trajectory] = Link(env, cells, edge, Cache())
  N[trajectory[0]]["out_links"].append(links[trajectory]) 
  N[trajectory[1]]["in_links"].append(links[trajectory])

for intersection_name in N:
  intersection = N[intersection_name]
  intersections[intersection_name] = Intersection(env, intersection_name, intersection["out_links"])

  # update links with newly created intersection
  for in_link in intersection["in_links"]:
    in_link.set_out_intersection(intersections[intersection_name])

# Generate cars using a specific traffic pattern. These patterns can be found in `traffic.py`.
traffic = Traffic(env, intersections, links)
env.process(traffic.get_traffic_strategy(args["strategy"], args["param"]))

# run the Simpy environment
env.run(until=args["until"])