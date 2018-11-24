import topology as topo
import simpy as sim
import numpy as np
from link import Link
from cache import Cache
from traffic import Traffic
from intersection import Intersection
from resource import Resource
import commandline

"""
Returns a mxn matrix containing 1-capacity resources, as well as the outgoing
intersection cells (m of them).
This matrix represents the cells where cars can be.
The resources have 1-capacity, so that only one car is present in one cell
 env: simpy environment
 m: number of lanes
 n: number of cells in one lane
"""
def initialize_road_cells(env, m, n):
  road_cells = np.array([[Resource(env) for j in range(n)] for i in range(m)])
  out_intersec_cells = [Resource(env) for _ in range(m)]

  return road_cells, out_intersec_cells

"""
Short-term stigmergy relies on the fact that this information is only available within a certain range.
To ensure this, we define a range (or radius) from a given intersection (`intersec`). If the Euclidian
distance from that intersection to any nodes is smaller or equal to that range, then all connected Links
to that other node is considered to be visible to `intersec`.
This is an implementation decision, as it was not explained in the paper.
"""
def get_visible_links_within_area(N, links, intersec, range):
  visibles = set()
  for start, end in links:
    if topo.dist(N[start]["pos"], intersec["pos"]) <= range or topo.dist(N[end]["pos"], intersec["pos"]) <= range:
      visibles.add(links[(start, end)])

  return visibles

args = commandline.parse()

N, E = topo.topology_parser(args["network"])

env = sim.RealtimeEnvironment()
links = {} # holds references to the links of the road network
intersections = {} # holds references to the intersections of the road network
for trajectory in E:
  edge = E[trajectory]
  road_cells, out_intersec_cells = initialize_road_cells(env, edge['lanes'], edge['cells'])

  stigmery_cache = Cache(env, edge['cells'])
  env.process(stigmery_cache.update_stigmery()) # define a process for the stigmergy caches so that they update over time
  links[trajectory] = Link(env, road_cells, out_intersec_cells, edge, stigmery_cache)
  N[trajectory[0]]["out_links"].append(links[trajectory]) 
  N[trajectory[1]]["in_links"].append(links[trajectory])

for intersection_name in N:
  intersection = N[intersection_name]
  visible_links = get_visible_links_within_area(N, links, intersection, args["range"])

  intersections[intersection_name] = Intersection(env, intersection_name, intersection["out_links"], visible_links)

  # update links with newly created intersection
  for in_link in intersection["in_links"]:
    in_link.set_out_intersection(intersections[intersection_name])

# Generate cars using a specific traffic pattern. These patterns can be found in `traffic.py`.
traffic = Traffic(env, intersections, links)
cars_proc = env.process(traffic.get_traffic_strategy(args["strategy"], args["param"]))

# run the Simpy environment
until = args["until"] if args["until"] else np.inf
env.run(until=env.any_of([cars_proc, env.timeout(until)]))