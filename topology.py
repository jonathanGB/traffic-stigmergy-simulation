import re
import numpy as np
from sys import exit

"""
Euclidian distance
 point1: (x1,y1)
 point2: (x2,y2)
"""
def dist(point1, point2):
  return np.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

"""
Return the random maximum speed for an edge.
The paper specifies that an arterial road (more than 1 lane) has a uniform vmax between 20 and 30 km/h,
while ordinary roads are sampled between 15 and 25 km/h.
 lanes: number of lanes forming the dge
"""
def get_vmax(lanes):
  return np.random.uniform(20, 30) if lanes > 1 else np.random.uniform(15, 25)

"""
Parse a topology defined in file `path`
 path: path to the topology file
"""
def topology_parser(path):
  vertices = {}
  edges = {}

  with open(path, encoding="utf-8") as file:
    x = [l.strip() for l in file]

    topo_iter = iter(x)
    line = next(topo_iter)
    while len(line) > 0:
      match = re.match(r'([a-zA-Z_0-9]+)\s*:\s*(\d+)\s*,\s*(\d+)', line)
      if not match:
        print("line wrongly formatted:\n\t", line)
        exit()
    
      vertex_name = match.group(1)
      x, y = int(match.group(2)), int(match.group(3))

      if vertex_name in vertices:
        print("vertex", vertex_name, "already used")
        exit()

      vertices[vertex_name] = (x,y)
      line = next(topo_iter)

    for line in topo_iter:
      match = re.match(r'([a-zA-Z_0-9]+)\s*:([a-zA-Z_0-9]+)\s*(\d+)\s*:(\d+)', line)
      if not match:
        print("line wrongly formatted:\n\t", line)
        exit()
    
      start, end = match.group(1), match.group(2)
      forward, backward = int(match.group(3)), int(match.group(4))

      if (start,end) in edges or (end,start) in edges:
        print(start,end, "is already an existing pair")
        exit()
      
      l = dist(vertices[start], vertices[end])
      if forward > 0:
        vmax_f = get_vmax(forward)
        cells_f = int(l/vmax_f)

        edges[(start,end)] = {
          "lanes": forward,
          "l": l,
          "vmax": vmax_f,
          "cells": cells_f,
          "cap": forward * cells_f
        }

      if backward > 0:
        vmax_b = get_vmax(backward)
        cells_b = int(l/vmax_b)

        edges[(end,start)] = {
          "lanes": backward,
          "l": l,
          "vmax": vmax_b,
          "cells": cells_b,
          "cap": backward * cells_b
        }

  return vertices, edges