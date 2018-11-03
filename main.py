import topology as topo
import simpy as sim
import numpy as np
from link import Link
from cache import Cache

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

# TODO: read command-line arguments to get the path to the topology file
N, E = topo.topology_parser("networks/network1.txt")

env = sim.RealtimeEnvironment()
links = {} # holds references to the links of the road network
for intersections in E:
  edge = E[intersections]
  cells = initialize_road_cells(env, edge['lanes'], edge['cells'])

  links[intersections] = Link(env, intersections, cells, edge, Cache())

# TODO: generate cars using a specific pattern. Probably have various pattern generators in a separate file.

# TODO: run the Simpy environment