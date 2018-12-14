import topology as topo
import simpy as sim
import numpy as np
from link import Link
from cache import Cache
from traffic import Traffic
from intersection import Intersection
from resource import Resource
from monitor import Monitor
import commandline
import multiprocessing as mp
from copy import deepcopy

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

def run(args):
  N, E = topo.topology_parser(args["network"])

  env = sim.Environment()
  monitor = Monitor(env)
  links = {} # holds references to the links of the road network
  intersections = {} # holds references to the intersections of the road network
  for trajectory in E:
    edge = E[trajectory]
    road_cells, out_intersec_cells = initialize_road_cells(env, edge['lanes'], edge['cells'])

    stigmery_cache = Cache(env, edge['cells'])
    env.process(stigmery_cache.update_stigmery()) # define a process for the stigmergy caches so that they update over time
    links[trajectory] = Link(env, road_cells, out_intersec_cells, edge, stigmery_cache, monitor, edge['has_stigmergy'])
    links[trajectory].register_to_monitor()
    links[trajectory].register_cells()
    N[trajectory[0]]["out_links"].append(links[trajectory]) 
    N[trajectory[1]]["in_links"].append(links[trajectory])

  for intersection_name in N:
    intersection = N[intersection_name]
    visible_links = get_visible_links_within_area(N, links, intersection, args["range"])

    intersections[intersection_name] = Intersection(env, intersection_name, intersection["out_links"], visible_links, intersection["pos"])
    monitor.register_intersection(intersections[intersection_name])
    
    # update links with newly created intersection
    for in_link in intersection["in_links"]:
      in_link.set_out_intersection(intersections[intersection_name])

    for out_link in intersection["out_links"]:
      out_link.set_in_intersection(intersections[intersection_name])

  # Generate cars using a specific traffic pattern. These patterns can be found in `traffic.py`.
  traffic = Traffic(env, intersections, links, monitor)
  cars_proc = env.process(traffic.get_traffic_strategy(args["traffic"], args["param"]))

  if args["draw"]:
    env.process(monitor.draw_network())

  # run the Simpy environment
  until = args["until"] if args["until"] else np.inf
  env.run(until=env.any_of([cars_proc, env.timeout(until)]))

  print("Finished running strategy", args["param"]["strategy"])
  monitor.output_stats(args["output_file"])


# main routine
args = commandline.parse()

if args["param"]["strategy"] == "all":
  args["draw"] = False # in multiprocessing, we don't draw or print (we want this to be as fast as possible)
  args["param"]["verbose"] = False

  strategies = ["case0", "case1", "case2", "case3", "case4", "case5"]
  procs = []

  for strat in strategies:
    new_args = deepcopy(args)
    new_args["param"]["strategy"] = strat
    new_args["output_file"] = "{}.json".format(strat)

    procs.append(mp.Process(target=run, args=(new_args,)))

  for proc in procs:
    proc.start()

  # wait for processes to finish running
  for proc in procs:
    proc.join()
else:
  run(args)