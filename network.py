import heapq
import numpy as np

def __default_weight_query(link):
  return link.get_weight()

def __get_visiting_path(curr_tup):
  links_to_visit = []

  while curr_tup:
    previous_node_tup, in_link = curr_tup[2], curr_tup[3]

    links_to_visit.append(in_link)
    curr_tup = previous_node_tup

  return links_to_visit[:-1]
  
# TODO: ADD COMENTS
# Returns a list of links to visit in order to get from the origin to the destination.
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