import heapq
import numpy as np

"""
Default query of the weight of a link.
We only use the number of cells of a lane in Case 0: no information
"""
def __default_weight_query(link):
  return link.get_weight()

"""
Query of the weight of a link based on its long-term stigmergy cost.
By default (until updated), long-term stigmergy cost is the same as its default weight.
"""
def case1_weight_query(link):
  return link.get_cache().get_long_term_stigmergy()

"""
Returns the list of links to visit (in reverse order) for the shortest path found using `shortest_path`.
"""
def __get_visiting_path(curr_tup):
  links_to_visit = []

  while curr_tup:
    previous_node_tup, in_link = curr_tup[2], curr_tup[3]

    links_to_visit.append(in_link)
    curr_tup = previous_node_tup

  return links_to_visit[:-1]
  
"""
Applies Dijkstra's shortest path from `start` to `end` in a given graph made of `links` (edges)
and `intersections` (nodes). A default parameters modulates how the weights of links are computed.
See `generate_blind_shortest_car` in `car.py` for an example of its call.
In the end, it returns [] if there is no path, otherwise, it returns the result of `__get_visiting_path`
  start: Intersection
  end: Intersection
  links: dictionary of Link
  intersections: dictionary of Intersection
  weight_link_query: function that computes the weight of a given link
"""
def shortest_path(start, end, links, intersections, weight_link_query=__default_weight_query):
  visited = set()
  intersection_mapper = {}

  to_visit = []
  for intersection_name in intersections:
    intersection = intersections[intersection_name]

    if intersection == start:
      tup = (0, start, None, None)
    else:
      tup = (np.inf, intersection, None, None)

    heapq.heappush(to_visit, tup)
    intersection_mapper[intersection] = tup

  while len(to_visit) > 0:
    visiting_tup = heapq.heappop(to_visit)
    visiting = visiting_tup[1]
    
    if visiting == end:
      return __get_visiting_path(visiting_tup)
    if visiting in visited:
      continue

    visited.add(visiting) # add the Intersection instance
    curr_node_weight = visiting_tup[0]
    outs = visiting.get_links()

    for out in outs:
      next_node = out.get_out_intersection()
      if next_node in visited:
        continue

      link_weight = weight_link_query(out)
      next_node_weight = intersection_mapper[next_node][0]

      if curr_node_weight + link_weight < next_node_weight:
        next_node_tup = (curr_node_weight + link_weight, next_node, visiting_tup, out)
        intersection_mapper[next_node] = next_node_tup
        heapq.heappush(to_visit, next_node_tup)

  return []